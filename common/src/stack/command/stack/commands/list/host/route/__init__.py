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
	List the static routes that are assigned to a host.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='list host route backend-0-0'>
	List the static routes assigned to backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.route', self._argv + ['scope=host']))
		return self.rc
