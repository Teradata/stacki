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
	Update known relationships between switches and hosts.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero or more switch names. If no switch names are supplied,
	all switches will be used.
	</arg>

	<example cmd="sync switch switch-0-0">
	Update known relationships between switch-0-0 and all hosts.
	</example>

	<example cmd="sync switch">
	Update known relationships between all switches and hosts.
	</example>
	"""
	def run(self, params, args):
		switches = self.getSwitchNames(args)

		self.beginOutput()
		for switch in self.call('list.switch', switches):
			switch_name = switch['switch']
			model = switch['model']
			self.runImplementation(model, [switch_name])

		self.endOutput()
