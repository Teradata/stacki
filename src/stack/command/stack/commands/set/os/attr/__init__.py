# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands

class Command(stack.commands.set.os.command):
	"""
	Sets an attribute to an os and sets the associated values 

	<arg type='string' name='os' optional='1' repeat='1'>
	Name of os
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
	"""

	def run(self, params, args):
		self.command('set.attr', self._argv + [ 'scope=os' ])
		return self.rc
