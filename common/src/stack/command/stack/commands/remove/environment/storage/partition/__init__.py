# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.environment.command):
	"""
	Remove storage partition information for an environment.

	<arg type='string' name='environment' repeat='1' optional='0'>
	An environment name.
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove environment storage partition test'>
	Removes the partition information for test environment scope.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		self.command('remove.storage.partition', self._argv + ['scope=environment'])
		return self.rc
