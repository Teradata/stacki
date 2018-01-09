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

		with stack.switch.SwitchDellX1052('192.168.2.1', 'admin', 'admin') as switch:
			switch.set_tftp_ip('192.168.2.10')
			switch.connect()
			switch.download()
			
			with open('/tftpboot/pxelinux/x1052_temp_download', 'r') as f:
				lines = f.readlines()
				_printline = True
				for line in lines:
					if 'crypto' in line:
						break

					if _printline:
						print(line, end='')

			print("switch config still WIP")

