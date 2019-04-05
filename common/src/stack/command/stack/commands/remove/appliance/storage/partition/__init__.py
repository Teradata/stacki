# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.appliance.command):
	"""
	Remove storage partition information for an appliance.

	<arg type='string' name='appliance' repeat='1' optional='0'>
	Appliance type (e.g., "backend").
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove appliance storage partition backend'>
	Removes the partition information for backend appliances
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		self.command('remove.storage.partition', self._argv + ['scope=appliance'])
		return self.rc
