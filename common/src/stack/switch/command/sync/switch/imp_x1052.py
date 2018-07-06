# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchException
from stack.switch.x1052 import SwitchDellX1052


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch_name = args[0]

		# Assume switch has only one entry in host interfaces
		interface = self.owner.call('list.host.interface', [switch_name])[0]

		# Get frontend ip for tftp address
		try:
			(frontend, *args) = [host for host in self.owner.call('list.host.interface', ['localhost'])
				if host['network'] == interface['network']]
		except:
			raise CommandError(self, '"%s" and the frontend do not share a network' % switch_name)

		frontend_tftp_address = frontend['ip']
		switch_address = interface['ip']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')

		# Connect to the switch
		with SwitchDellX1052(switch_address, switch_name, switch_username, switch_password) as _switch:
			_switch.set_tftp_ip(frontend_tftp_address)
			try:
				_switch.connect()
				_switch.upload()
				if self.owner.persistent:
					_switch.apply_configuration()
			except SwitchException as switch_error:
				raise CommandError(self, switch_error)
			except Exception as found_error:
				raise CommandError(self, "There was an error syncing the switch")
