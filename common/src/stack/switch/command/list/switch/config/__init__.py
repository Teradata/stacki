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
	List the running-config for the switch.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplied, info about
	all the known switches is listed.
	</arg>

	<param optional='1' type='string' name='raw'>
	If set, print out the raw config from the switch and not the table view.
	</param>

	<example cmd='list switch config switch-0-0'>
	List running-config for switch-0-0.
	</example>

	<example cmd='list switch'>
	List running-config for all known switches.
	</example>

	<example cmd='list switch config switch-0-0 raw=true'>
	List raw running-config for switch-0-0.
	</example>
	"""
	def run(self, params, args):

		(raw,) = self.fillParams([
			('raw', False),
			])

		raw = self.str2bool(raw)

		_switches = self.getSwitchNames(args)

		# Begin standard output if raw is False
		if not raw:
			self.beginOutput()

		for switch in self.call('list.host.interface',  _switches):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']

			# Connect to the switch
			with stack.switch.SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.download()
				
				with open('/tftpboot/pxelinux/%s_running_config' % switch_name, 'r') as f:
					lines = f.readlines()
					_printline = True
					_block = {}
					for line in lines:
						if not raw:
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
									self.addOutput(
										switch_name,[
										_block['port'],
										_block['vlan'],
										_block['type'],]
										)
								except:
									pass
								_block = {}

						else:
							if _printline:
								print(line, end='')

		if not raw:
			self.endOutput(header=[
				'switch',
				'port',
				'vlan',
				'type',
				])

