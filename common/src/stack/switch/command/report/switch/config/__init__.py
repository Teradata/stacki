# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.exception import CommandError

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.report.command,
	      stack.commands.HostArgumentProcessor):
	pass

class Command(command):
	"""
	Output the current configuration of the switch.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplied, info about
	all the known switches is listed.
	</arg>

	<example cmd='report switch config switch-0-0'>
	Output configuration for switch-0-0.
	</example>

	<example cmd='report switch config'>
	Output configuration for all known switches.
	</example>
	"""
	def run(self, params, args):

		switches = self.getSwitchNames(args)

		self.beginOutput()

		for switch in self.call('list.host.interface', switches):
			switch_name = switch['host']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [switch])

		self.endOutput(padChar='', trimOwner=True)

