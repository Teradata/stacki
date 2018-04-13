# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchDellX1052, SwitchException


class Implementation(stack.commands.Implementation):
	def run(self, args):

		switch = args[0]

		# Get frontend ip for tftp address
		try:
			(_frontend, *args) = [host for host in self.owner.call('list.host.interface', ['localhost'])
					if host['network'] == switch['network']]
		except:
			raise CommandError(self, '"%s" and the frontend do not share a network' % switch['host'])

		frontend_tftp_address	= _frontend['ip']
		switch_address		= switch['ip']
		switch_name		= switch['host']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')

		# Connect to the switch
		with SwitchDellX1052(switch_address, switch_name, switch_username, switch_password) as switch:
			try:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.download()
			
				with open('/tftpboot/pxelinux/%s_running_config' % switch_name, 'r') as f:
					lines = f.readlines()
					_printline = True
					_block = {}
					for line in lines:
						if not self.owner.raw:
							if 'crypto' in line:
								break

							if 'gigabitethernet' in line:
								_block['port'] = line.split('/')[-1].strip()

							if 'switchport' in line and 'access' in line:
								_, _type, _, _vlan = line.split()
								_block['type'] = _type
								_block['vlan'] = _vlan

							if '!' in line and _block:
								try:
									self.owner.addOutput(
										switch_name,[
										_block['port'],
										_block['vlan'],
										_block['type'],]
										)
								except:
									pass
								_block = {}

						# This is the line that gets hit if raw=true
						else:
							if _printline:
								print(line, end='')
			except SwitchException as switch_error:
				raise CommandError(self, switch_error)
			except Exception:
				raise CommandError(self, "There was an error downloading the running config from the switch")
