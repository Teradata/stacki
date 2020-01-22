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


class Command(stack.commands.list.os.command):
	"""
	List the routes for one of more OS

	<arg optional='1' type='string' name='os' repeat='1'>
	Zero, one or more os.
	</arg>

	<example cmd='list os route redhat'>
	Lists the routes for redhat OS.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.route', self._argv + ['scope=os'], verbose_errors = False))
		return self.rc
