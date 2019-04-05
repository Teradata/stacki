# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.list.os.command):
	"""
	List the storage partition configuration for a given OS(es).

	<arg optional='1' type='string' name='os' repeat='1'>
	Zero, one or more OS names. If no OS names are supplied,
	the routes for all the OSes are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=os']))
		return self.rc
