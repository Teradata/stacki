# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.commands
from stack.switch.e1050 import SwitchCelesticaE1050
import subprocess


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch_interface = args[0]

		self.switch_address = switch_interface['ip']
		self.switch_name = switch_interface['host']
		self.switch_username = self.owner.getHostAttr(self.switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(self.switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, self.switch_name, self.switch_username, switch_password)

		if self.owner.pinghosts in [self.owner._NETWORK, self.owner._MAPPED]:
			host_ifaces = self.ping_hosts()
		else:
			host_ifaces = self.owner.call('list.host.interface', ['where appliance != "switch"'])

		bridge_macs = self.switch.run('show bridge macs dynamic json', json_loads=True)
		for bridge_mac in sorted(bridge_macs, key=lambda d: d['dev']):
			mac = bridge_mac['mac']
			port = re.search(r'\d+', bridge_mac['dev']).group()
			vlan = bridge_mac['vlan'] if bridge_mac['vlan'] != 1 else None

			for iface in host_ifaces:
				if iface['mac'] == mac:
					host = iface['host']
					interface = iface['interface']

					self.owner.addOutput(self.switch_name, [port, mac, host, interface, vlan])
					break

	def ping_hosts(self):
		host_ifaces = self.owner.call('list.host.interface', ['where appliance != "switch"'])

		if self.owner.pinghosts == self.owner._NETWORK:
			network = self.owner.call('list.host.interface', [self.switch_name])[0]['network']
			host_ifaces = [iface for iface in host_ifaces if iface['network'] == network]
		elif self.owner.pinghosts == self.owner._MAPPED:
			switch_hosts = self.owner.call('list.switch.host', [self.switch_name])
			macs = [host['mac'] for host in switch_hosts]
			host_ifaces = [iface for iface in host_ifaces if iface['mac'] in macs]

		# ensure ssh key is copied to switch before running ping commands over ssh
		self.switch.ssh_copy_id()

		for iface in host_ifaces:
			subprocess.Popen(f'ssh {self.switch_username}@{self.switch_address} ping -c 1 {iface["ip"]}'.split(),
					 stdout=subprocess.PIPE)

		return host_ifaces

