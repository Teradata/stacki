# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.commands
from stack.switch.e1050 import SwitchCelesticaE1050


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch = args[0]

		switch_name = switch['host']
		switch_address = switch['ip']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')

		# better to get hosts from switch hostfile? also, 'net show bridge macs <ip>' suggests switch knows host ip
		hosts = self.owner.call('list.host.interface', ['output-format=json'])

		with SwitchCelesticaE1050(switch_address, switch_name, switch_username, switch_password) as switch:
			# better names?
			bridge_macs = {}
			for entry in switch.json_loads(cmd="show bridge macs dynamic json"):  # pinghosts=True (broken)
				interface_name = entry.pop('dev')  # why did they call iface 'dev'?
				# TODO: clean up formatting
				if 'swp' in interface_name \
					and (interface_name not in bridge_macs
					     or entry['updated'] < bridge_macs[interface_name]['updated']):
					bridge_macs[interface_name] = entry

			interfaces = switch.json_loads(cmd="show interface json")
			switch_ports = (interface_name for interface_name in interfaces if 'swp' in interface_name)
			for interface_name in switch.sorted_keys(switch_ports):
				try:
					bridge_mac = bridge_macs[interface_name]
					mac = bridge_mac['mac']
					vlan = bridge_mac['vlan']  # should vlan come from FE or switch? Missing from FE atm

					for host_obj in hosts:
						if host_obj['mac'] == mac:
							host = host_obj['host']
							interface = host_obj['interface']
							break
					else:
						host = ''
						interface = ''
				except KeyError:
					host = ''
					interface = ''
					mac = ''
					vlan = ''

				port = re.search(r'\d+', interface_name).group()
				speed = interfaces[interface_name]['speed']
				state = interfaces[interface_name]['linkstate']

				self.owner.addOutput(switch_name, [port, speed, state, mac, vlan, host, interface])

