# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.commands
from stack.switch.e1050 import SwitchCelesticaE1050


# similar to 'list switch status'; intentional? reusable?
class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch = args[0]

		switch_name = switch['host']
		switch_address = '10.2.232.32'  # temporary
		#switch_address = switch['ip']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')

		# better to get hosts from switch hostfile? also, 'net show bridge macs <ip>' suggests switch knows host IP
		hosts = self.owner.call('list.host.interface', ['output-format=json'])
		with SwitchCelesticaE1050(switch_address, switch_name, switch_username, switch_password) as switch:
			# better name(s)?
			for iface_obj in sorted(switch.json_loads(cmd='show bridge macs dynamic json'), key=lambda d: d['dev']):  # why did they call iface 'dev'?
				mac = iface_obj['mac']
				port = re.search(r'\d+', iface_obj['dev']).group()
				vlan = iface_obj['vlan']  # should VLAN come from FE or switch?

				matching_hosts = (host_obj for host_obj in hosts if host_obj['mac'] == mac)
				for host_obj in matching_hosts:
					host = host_obj['host']
					interface = host_obj['interface']

					self.owner.addOutput(switch_name, [port, mac, host, interface, vlan])
					break

