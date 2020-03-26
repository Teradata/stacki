# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import subprocess

import stack.commands
from stack.commands import SwitchArgProcessor
from stack.exception import CommandError
import stack.util

class command(SwitchArgProcessor, stack.commands.sync.command):
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

	<param type='boolean' name='nukeswitch' optional='1'>
	If 'yes', then put the switch into a default state (e.g., no vlans, no partitions),
	Just a "flat" switch.
	Default: no
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

		persistent, nukeswitch = self.fillParams([
			('persistent', 'yes'),
			('nukeswitch', 'no'),
		])
		self.persistent = self.str2bool(persistent)
		self.nukeswitch = self.str2bool(nukeswitch)

		switches = self.getSwitchNames(args)

		for switch in self.call('list.host.interface', switches):
			switch_name = switch['host']

			self.report('report.switch', [ switch_name ])
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [switch])

