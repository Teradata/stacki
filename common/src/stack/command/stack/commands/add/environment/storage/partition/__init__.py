# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.add.environment.command):
	"""
	Add a storage partition configuration for an environment.

	<arg type='string' name='environment' repeat='1' optional='0'>
	An environment name.
	</arg>

	<param type='string' name='device' optional='0'>
	Disk device on which we are creating partitions
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint to create
	</param>

	<param type='integer' name='size' optional='0'>
	Size of the partition.
	</param>

	<param type='string' name='type' optional='1'>
	Type of partition E.g: ext4, ext3, xfs, raid, etc.
	</param>

	<param type='string' name='options' optional='1'>
	Options that need to be supplied while adding partitions.
	</param>

	<param type='integer' name='partid' optional='1'>
	The relative partition id for this partition. Partitions will be
	created in ascending partition id order.
	</param>

	<example cmd='add environment storage partition test device=sda mountpoint=/var size=50 type=ext4'>
	Creates a ext4 partition on device sda with mountpoints /var in the test environment scope.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		self.command('add.storage.partition', self._argv + ['scope=environment'])
		return self.rc
