# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
import stack.switch

class command(stack.commands.SwitchArgumentProcessor,
	stack.commands.list.command):
	pass

class Command(command):
	"""
	"""
	def run(self, params, args):

		_switches = self.getSwitchNames(args)
		for switch in self.call('list.host.interface', _switches):

			# Get frontend ip for tftp address
			frontend, *xargs = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			frontend_tftp_address = frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']
			with stack.switch.SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.set_filenames(switch_name)
				switch.connect()
				switch.get_vlan_table()
				
				with open('/tmp/%s_vlan_table' % switch_name, 'r') as f:
					lines = f.readlines()
					_printline = False
					for line in lines:
						if 'Vlan' in line or 'gi1/0/' in line:
							_printline = True
						if ',' not in line or not line or 'space' in line:
							_printline = False
						if'console' in line:
							break

						if _printline:
							print(line, end='')
