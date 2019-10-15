# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.host.command):
	"""
	Remove storage partition configuration for a host.

	<arg type='string' name='host' repeat='1' optional='0'>
	Hostname of the machine
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove host storage partition backend-0-1'>
	Removes the partition information for backend-0-1
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		self.command('remove.storage.partition', self._argv + ['scope=host'])
		return self.rc
