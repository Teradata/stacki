# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.switch.e1050 import SwitchCelesticaE1050


# is /tftpboot/pxelinux/stacki-232-32_running_config supposed to exist on FE? If so, 'show configuration' is irrelevant
class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch = args[0]

		switch_name = switch['host']
		switch_address = switch['ip']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')

		with SwitchCelesticaE1050(switch_address, switch_name, switch_username, switch_password) as switch:
			text = switch.rpc_req_text("show configuration")

			if self.owner.raw:
				print(text)  # just print for raw?
			else:
				# data = json.loads(text)
				self.owner.addOutput(switch_name, [])  # port, vlan, type -- these headers don't map well to the raw text
