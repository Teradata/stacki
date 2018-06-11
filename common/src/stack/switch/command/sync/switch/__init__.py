# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
import stack.switch
import subprocess
from stack.exception import CommandError

class command(stack.commands.SwitchArgumentProcessor,
	stack.commands.sync.command):
		pass

class Command(command):
	"""
	Reconfigure switch and optionally set the configuration 
	to the startup configuration.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplied,
	all switches will be reconfigured.
	</arg>

	<param type='boolean' name='persistent'>
	If "yes", then set the startup configuration.
	The default is: yes.
	</param>

	<example cmd="sync switch switch-0-0">
	Reconfigure and set startup configuration on switch-0-0.
	</example>

	<example cmd="sync switch switch-0-0 persistent=no">
	Reconfigure switch-0-0 but dont set the startup configuration..
	</example>

	<example cmd="sync switch">
	Reconfigure and set startup configuration on all switches.
	</example>
	"""
	def run(self, params, args):

		persistent, = self.fillParams([
			('persistent', False)
			])

		self.persistent = self.str2bool(persistent)

		switches = self.getSwitchNames(args)

		# Run report switch
		self.report('report.switch')

		for switch in self.call('list.host.interface', switches):

			switch_name = switch['host']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [switch])
