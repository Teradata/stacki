# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
import stack.switch

class command(stack.commands.HostArgumentProcessor,
	stack.commands.list.command):
	pass

class Command(command):
	"""
	"""
	def run(self, params, args):

		hosts = self.getHostnames(args)
		_switches = self.call('list.switch', hosts)
		for switch in self.call('list.host.interface', [s['host'] for s in _switches]):

			# Get frontend ip for tftp address
			_frontend, = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			with stack.switch.SwitchDellX1052(switch_address, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.download()
				
				with open('/tftpboot/pxelinux/x1052_temp_download', 'r') as f:
					lines = f.readlines()
					_printline = False
					for line in lines:
						if 'set system' in line or 'interface vlan' in line:
							_printline = True
						if 'gigabitethernet' in line or 'exit':
							_printline = False
						if 'crypto' in line:
							break

						if _printline:
							print(line, end='')

				print("switch config still WIP")
RollName = "stacki"
