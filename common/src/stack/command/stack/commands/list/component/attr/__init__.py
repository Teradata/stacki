# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Command(stack.commands.list.component.command):
	"""
	Lists the set of attributes for a component.

	<arg optional='1' type='string' name='component'>
	Component name of machine
	</arg>
	
	<param type='string' name='attr'>
	A shell syntax glob pattern to specify to attributes to
	be listed.
	</param>

	<example cmd='list component attr backend-0-0'>
	List the attributes for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.attr', self._argv + [ 'scope=component' ]))
		return self.rc

