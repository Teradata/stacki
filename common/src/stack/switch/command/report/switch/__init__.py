# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 

import re
import stack.commands

class command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command,
	stack.commands.DatabaseConnection):
	pass

class Command(command):
	"""
	Output the switch configuration file.

	<example cmd='report switch ethernet-1-1'>
	Output the configation file for ethernet-1-1.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()

		for switch in self.call('list.switch', args):
			
			switch_name = switch['switch']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [ switch ])

		self.endOutput(padChar='', trimOwner=True)
