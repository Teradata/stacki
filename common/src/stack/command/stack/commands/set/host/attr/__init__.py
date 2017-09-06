# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands

class Command(stack.commands.set.host.command):
	"""
	Sets an attribute to a host and sets the associated values 

	<arg type='string' name='host' optional='1' repeat='1'>
	Host name of machine
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

	<example cmd='set host attr backend-0-0 attr=cpus value=2'>
	Sets the number of cpus of backend-0-0 to 2
	</example>
	"""

	def run(self, params, args):

		argv = args
		argv.append('scope=host')
		for p in params:
			argv.append('%s=%s' % (p, params[p]))

		self.command('set.attr', argv)

