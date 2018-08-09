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

		switch_hosts = self.owner.call('list.switch.host', [switch_name])

		with SwitchCelesticaE1050(switch_address, switch_name, switch_username, switch_password) as switch:
			interfaces = switch.run("show interface json", json_loads=True)
			for switch_host in switch_hosts:
				interface = interfaces[f'swp{switch_host["port"]}']
				port = switch_host['port']
				speed = interface['speed']
				state = interface['linkstate']
				mac = switch_host['mac']
				vlan = switch_host['vlan']
				host = switch_host['host']
				interface = switch_host['interface']

				self.owner.addOutput(switch_name, [port, speed, state, mac, vlan, host, interface])

