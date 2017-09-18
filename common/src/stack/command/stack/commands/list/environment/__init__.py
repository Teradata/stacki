# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class command(stack.commands.EnvironmentArgumentProcessor,
	stack.commands.list.command):
	pass


class Command(command):
	"""
	Lists the environments defined.
	
	<arg optional='1' type='string' name='environment' repeat='1'>
	Optional list of environment names.
	</arg>
		
	<example cmd='list environment'>
	List all known environments.
	</example>
	"""

	def run(self, params, args):
		
		self.beginOutput()
		for env in self.getEnvironmentNames(args):
			self.addOutput(env, None)
			
		self.endOutput(header=['environment'])
	
