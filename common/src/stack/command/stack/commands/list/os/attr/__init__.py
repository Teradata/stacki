# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@


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

