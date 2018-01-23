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
	Remove a new host with appliance type 'switch' from the cluster.

	<arg type='string' name='switch'>
	A single switch/host name. 
	</arg>

	"""

	def run(self, params, args):

		if len(args) < 1:
			raise ArgRequired(self, 'switch')
		
		switches = self.getSwitchNames(args)

		self.call('remove.host', switches)
