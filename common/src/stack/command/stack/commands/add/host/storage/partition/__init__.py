# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.add.host.command):
	"""
	Add a storage partition configuration for the specified hosts.

	<arg type='string' name='host' repeat='1' optional='0'>
	Host name of machine
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

	<example cmd='add host storage partition backend-0-0 device=sda mountpoint=/var size=50 type=ext4'>
	Creates a ext4 partition on device sda with mountpoints /var.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		self.command('add.storage.partition', self._argv + ['scope=host'])
		return self.rc
