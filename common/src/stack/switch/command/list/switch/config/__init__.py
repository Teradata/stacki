# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.exception import CommandError

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
		self.raw = raw

		_switches = self.getSwitchNames(args)

		# Begin standard output if raw is False
		if not raw:
			self.beginOutput()

		for switch in self.call('list.host.interface',  _switches):

			switch_name = switch['host']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [switch])

		if not raw:
			self.endOutput(header=[
				'switch',
				'port',
				'vlan',
				'type',
				])

