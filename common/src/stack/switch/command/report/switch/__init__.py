# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 

import re

import stack.commands
from stack.commands import HostArgProcessor

class command(HostArgProcessor,
	stack.commands.report.command,
	stack.commands.DatabaseConnection):
	pass

class Command(command):
	"""
	Output the switch configuration file.

	<arg type='string' name='switch'>
	Name of the switch. If no switches are supplied, then output the report for all switches.
	</arg>

	<param type='boolean' name='nukeswitch' optional='1'>
	If 'yes', then put the switch into a default state (e.g., no vlans, no partitions),
	Just a "flat" switch.
	Default: no
	</param>

	<example cmd='report switch ethernet-1-1'>
	Output the configation file for ethernet-1-1.
	</example>
	"""

	def run(self, params, args):
		nukeswitch, = self.fillParams([ ('nukeswitch', 'n') ])

		self.nukeswitch = self.str2bool(nukeswitch)

		self.beginOutput()

		for switch in self.call('list.switch', args):
			
			switch_name = switch['switch']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [ switch ])

		self.endOutput(padChar='', trimOwner=True)
