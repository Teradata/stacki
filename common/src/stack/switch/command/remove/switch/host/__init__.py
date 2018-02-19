# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError, ArgRequired

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.remove.command):
	pass

class Command(command):
	"""
	Stop managing a host connected to a switch.

	<arg type='string' name='switch'>
	The switch you are going to remove the host from.
	</arg>

	<param optional='0' type='string' name='host'>
	The name of the host you want to stop managing.
	</param>

	"""

	def run(self, params, args):

		if len(args) < 1:
			raise ArgRequired(self, 'switch')
		
		switch, = self.getSwitchNames(args)

		host, = self.fillParams([
			('host', None, True),
			])

		self.delSwitchHost(switch, host)
