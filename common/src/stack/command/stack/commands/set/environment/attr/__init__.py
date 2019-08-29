# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.set.environment.command):
	"""
	Sets an attribute to an environment and sets the associated values

	<arg type='string' name='environment' optional='0' repeat='1'>
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
		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		self.command('set.attr', self._argv + ['scope=environment'])
		return self.rc
