# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.remove.os.command):
	"""
	Remove an attribute for an OS.

	<arg type='string' name='os' optional='1' repeat='1'>
	One or more OS specifications (e.g., 'linux').
	</arg>

	<param type='string' name='attr' optional='0'>
	The attribute name that should be removed.
	</param>

	<example cmd='remove os attr linux attr=sge'>
	Removes the attribute sge for linux OS machines.
	</example>
	"""

	def run(self, params, args):
		self.command('remove.attr', self._argv + ['scope=os'])
		return self.rc
