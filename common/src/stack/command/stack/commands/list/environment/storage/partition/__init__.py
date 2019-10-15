# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.list.environment.command):
	"""
	List the storage partition configuration for one or more environments.

	<arg optional='1' type='string' name='environment' repeat='1'>
	Zero, one or more environments.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=environment']))
		return self.rc
