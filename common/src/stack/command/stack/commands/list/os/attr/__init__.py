# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands


class Command(stack.commands.list.os.command):
	"""
	Lists the set of attributes for OSes.

	<arg optional='1' type='string' name='os'>
	Name of OS (e.g. "linux", "sunos") 
	</arg>
	
	<example cmd='list os attr linux'>
	List the attributes for the Linux OS
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.attr', self._argv + [ 'scope=os' ]))
		return self.rc

