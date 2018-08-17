# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import subprocess
import stack.commands
from stack.exception import CommandError
from stack.switch.e1050 import SwitchCelesticaE1050


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch_interface = args[0]

		self.switch_address = switch_interface['ip']
		self.switch_name = switch_interface['host']
		self.switch_username = self.owner.getHostAttr(self.switch_name, 'switch_username')
		self.switch_password = self.owner.getHostAttr(self.switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, self.switch_name,
						   self.switch_username, self.switch_password)

		self.switch.ssh_copy_id()
		self.add_routes()

		try:
			for command in open(f'/tmp/{self.switch_name}/new_config').readlines():
				self.switch.run(command.strip())

			#print(self.switch.run('pending'))
			self.switch.run('commit')
		except:
			self.switch.run('abort')
			raise CommandError(self, 'sync failed')
		finally:
			subprocess.run(f'rm -rf /tmp/{self.switch_name}'.split(), stdout=subprocess.PIPE)

	def add_routes(self):
		networks = {network['network']: network for network in self.owner.call('list.network')}
		switch_networks = set()

		base_network_name = [interface['network'] for interface in
				     self.owner.call('list.host.interface', [self.switch_name])
				     if interface['default']][0]
		base_network = networks[base_network_name]

		frontend_interface = [interface for interface in self.owner.call('list.host.interface', ['localhost'])
				      if interface['network'] == base_network_name][0]
		frontend_name = frontend_interface['host']
		frontend_device = frontend_interface['interface']

		for interface in self.owner.call('list.switch.host', [self.switch_name]):
			host = interface['host']
			if host == frontend_name:
				continue

			device = interface['interface']
			# better to do these SELECTs or to dict-ify `list host interface`?
			((vlan_network_name, ), ) = self.db.select("""name FROM subnets WHERE
								ID=(SELECT Subnet FROM networks WHERE
								Node=(SELECT ID from nodes WHERE Name=%s) AND
								Device=%s)""", (host, device))
			if vlan_network_name == base_network_name:
				continue

			vlan_network = networks[vlan_network_name]
			switch_networks.add(vlan_network_name)

			address = base_network['address']
			gateway = vlan_network['gateway']
			mask = base_network['mask']
			try:
				self.owner.call('add.host.route', f'{host} address={address} gateway={gateway} '
								  f'interface={device} netmask={mask}'.split())
			except CommandError:
				# route already exists
				continue

		for vlan_network_name in switch_networks:
			vlan_network = networks[vlan_network_name]

			address = vlan_network['address']
			gateway = base_network['gateway']
			interface = frontend_device
			netmask = vlan_network['mask']

			try:
				self.owner.call('add.host.route', f'localhost address={address} gateway={gateway} '
								  f'interface={interface} netmask={mask}'.split())
			except CommandError:
				# route already exists
				continue

		# `sync host network localhost`?

