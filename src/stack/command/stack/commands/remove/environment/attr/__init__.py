# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands
from stack.exception import *

class Command(stack.commands.remove.environment.command):
	"""
	Remove an attribute for an Environment.

	<arg type='string' name='environment' repeat='1' optional='1'>
	One or more Environment specifications (e.g., 'test').
	</arg>
	
	<param type='string' name='attr' optional='0'>
	The attribute name that should be removed.
	</param>
	
	<example cmd='remove environment attr test attr=sge'>
	Removes the attribute sge for text environment machines.
	</example>
	"""

	def run(self, params, args):
		self.command('set.attr', self._argv + [ 'scope=environment', 'value=' ])
		return self.rc
