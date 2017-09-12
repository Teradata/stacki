# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands


class Command(stack.commands.list.environment.command):
	"""
	Lists the set of attributes for environments.

	<arg optional='1' type='string' name='environment'>
	Name of environment (e.g. "test") 
	</arg>
	
	<example cmd='list environment attr test'>
	List the attributes for the test environment
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.attr', self._argv + [ 'scope=environment' ]))
		return self.rc
