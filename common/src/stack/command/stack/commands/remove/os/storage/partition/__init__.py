# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.os.command):
	"""
	Remove storage partition configuration for an OS type.

	<arg type='string' name='os' repeat='1' optional='0'>
	OS type (e.g., 'redhat', 'sles').
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove os storage partition redhat'>
	Removes the partition information for redhat os type
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'os')

		self.command('remove.storage.partition', self._argv + ['scope=os'])
		return self.rc
