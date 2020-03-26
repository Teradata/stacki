# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import HostArgProcessor, SwitchArgProcessor
from stack.exception import CommandError, ArgRequired

class command(HostArgProcessor, SwitchArgProcessor, stack.commands.remove.command):
	pass

class Command(command):
	"""
	Stop managing a host connected to a switch.

	<arg type='string' name='switch'>
	The switch you are going to remove the host from.
	</arg>

	<param type='string' name='host' optional='0'>
	Name of the host (e.g., backend-0-0).
	</param>

	<param type='string' name='port' optional='0'>
	Port on the switch the host is connected to (e.g., 4).
	</param>

	<param type='string' name='interface' optional='0'>
	Name of the host's interface that is connected to the switch (e.g., 'eth0').
	</param>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'switch')

		switch, = self.getSwitchNames(args)

		host, port, interface = self.fillParams([
			('host', None, True),
			('port', None, True),
			('interface', None, True)
		])

		# Check if host exists
		self.getHostnames([host])

		self.delSwitchHost(switch, port, host, interface)
