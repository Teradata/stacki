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

		self.owner.addOutput('localhost', f'<stack:file stack:name="/tmp/{switch_name}/current_config">')

		with SwitchCelesticaE1050(switch_address, switch_name, switch_username, switch_password) as switch:
			text = switch.run("show configuration commands")
			for line in text.split('\n'):
				# fix switch bug in showing `add vlan`
				if line.startswith('net add vlan vlan'):
					line = line[:13] + line[17:]

				# nclu *does* support adding routes
				if line.startswith("sudo printf 'vrf Default-IP-Routing-Table"):
					network = re.search(r'\d+\.\d+\.\d+\.\d+/\d+', line).group(0)
					vlan = re.search(r'vlan\d+', line).group(0)

					line = f'net add routing route {network} {vlan}'

				self.owner.addOutput('localhost', line)

		self.owner.addOutput('localhost', '</stack:file>')

