# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.set.environment.command):
	"""
	Sets an attribute to an environment and sets the associated values 

	<arg type='string' name='environment' repeat='1'>
	Name of environment
	</arg>
	
	<param type='string' name='attr' optional='0'>
	Name of the attribute
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>
	
	<param type='boolean' name='shadow'>
	If set to true, then set the 'shadow' value (only readable by root
	and apache).
	</param>

	<example cmd='set environment attr test sge False'>
	Sets the sge attribution to False for test nodes
	</example>

	"""

	def run(self, params, args):

		argv = args
		argv.append('scope=environment')
		for p in params:
			argv.append('%s=%s' % (p, params[p]))

		self.command('set.attr', argv)


