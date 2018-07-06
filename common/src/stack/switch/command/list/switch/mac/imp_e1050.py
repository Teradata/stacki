# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import pexpect
import re
import stack.commands
from stack.switch.e1050 import SwitchCelesticaE1050


# similar to 'list switch status'; intentional? reusable?
class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch_name = args[0]

		self.svis = self.owner.call('list.host.interface', [switch_name])
		access_interface = [svi for svi in self.svis if not svi['vlan']][0]  # temporary

		self.switch_address = access_interface['ip']
		self.switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, switch_name, self.switch_username, switch_password)

		if self.owner.pinghosts:
			self.ping_hosts()

		# better to get hosts from switch hostfile? also, 'net show bridge macs <ip>' suggests switch knows host IP
		hosts = self.owner.call('list.host.interface', ['where appliance != "switch"'])
		# better name(s)?
		for iface_obj in sorted(self.switch.json_loads(cmd='show bridge macs dynamic json'), key=lambda d: d['dev']):  # why did they call iface 'dev'?
			mac = iface_obj['mac']
			port = re.search(r'\d+', iface_obj['dev']).group()
			vlan = iface_obj['vlan']  # should VLAN come from FE or switch?

			matching_hosts = (host_obj for host_obj in hosts if host_obj['mac'] == mac)
			for host_obj in matching_hosts:
				host = host_obj['host']
				interface = host_obj['interface']

				self.owner.addOutput(switch_name, [port, mac, host, interface, vlan])
				break

	def ping_hosts(self):
		child = pexpect.spawn(f'ssh {self.switch_username}@{self.switch_address}')
		hosts = self.owner.call('list.host.interface', ['where appliance != "frontend" and appliance != "switch"'])
		networks = [interface['network'] for interface in self.svis]
		try:
			for host in (host for host in hosts if host['network'] in networks):
				child.expect('#')
				child.sendline(f'ping -c 1 {host["ip"]}')
		except pexpect.EOF as e:
			print('shit')
			raise e

