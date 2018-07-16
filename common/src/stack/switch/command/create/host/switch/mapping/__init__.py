# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired

class command(stack.commands.HostArgumentProcessor, stack.commands.SwitchArgumentProcessor, stack.commands.create.command):
	pass

class Command(command):
	"""
	This command dynamically maps the interfaces of hosts to ports of a switch.

	<arg name="host">
	The hosts to map. If no hosts are supplied, map all hosts.
	</arg>

	<param type='string' name='switch'>
	The switch to map. If no switches are supplied, then map all switches.
	</param>
	"""

	def run(self, params, args):
		switch, = self.fillParams([ ('switch', None) ])

		switches = self.getSwitchNames(switch)
		hosts = self.getHostnames(args)

		for s in switches:
			model = self.getHostAttr(s, 'component.model')
			if model in ['e1050', 'x1052']:
				model = 'default'

			self.runImplementation(model, (s, hosts))

