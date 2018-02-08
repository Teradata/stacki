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
	List vlan table on switch.

	Still experimental.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplies, info about
	all the known switches is listed.
	</arg>

	<example cmd='list host switch-0-0'>
	List vlan info for switch-0-0.
	</example>

	<example cmd='list switch'>
	List vlan info for all known switches.
	</example>
	"""
	def run(self, params, args):

		_switches = self.getSwitchNames(args)
		for switch in self.call('list.host.interface', _switches):

			# Get frontend ip for tftp address
			try:
				(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost'])
						if host['network'] == switch['network']]
			except:
				raise CommandError(self, '"%s" and the frontend do not share a network' % switch['host'])

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
