# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


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
		self.command('remove.attr', self._argv + ['scope=environment'])
		return self.rc
