# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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


class Command(stack.commands.list.host.command):
	"""
	Lists the set of attributes for hosts.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='attr'>
	A shell syntax glob pattern to specify to attributes to
	be listed.
	</param>

	<example cmd='list host attr backend-0-0'>
	List the attributes for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.attr', self._argv + [ 'scope=host' ]))
		return self.rc

