# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.add.os.command):
	"""
	Add a storage controller configuration for an OS type.

	<arg type='string' name='os' repeat='1' optional='0'>
	OS type (e.g., 'redhat', 'sles').
	</arg>

	<param type='integer' name='adapter' optional='1'>
	Adapter address.
	</param>

	<param type='integer' name='enclosure' optional='1'>
	Enclosure address.
	</param>

	<param type='integer' name='slot'>
	Slot address(es). This can be a comma-separated list meaning all disks
	in the specified slots will be associated with the same array
	</param>

	<param type='integer' name='raidlevel'>
	RAID level. Raid 0, 1, 5, 6, 10, 50, 60 are currently supported.
	</param>

	<param type='integer' name='hotspare' optional='1'>
	Slot address(es) of the hotspares associated with this array id. This
	can be a comma-separated list (like the 'slot' parameter). If the
	'arrayid' is 'global', then the specified slots are global hotspares.
	</param>

	<param type='string' name='arrayid' optional='0'>
	The 'arrayid' is used to determine which disks are grouped as part
	of the same array. For example, all the disks with arrayid of '1' will
	be part of the same array. Arrayids must be integers starting at 1
	or greater. If the arrayid is 'global', then 'hotspare' must
	have at least one slot definition (this is how one specifies a global
	hotspare).

	In addition, the arrays will be created in arrayid order, that is,
	the array with arrayid equal to 1 will be created first, arrayid
	equal to 2 will be created second, etc.
	</param>

	<example cmd='add os storage controller sles slot=1 raidlevel=0 arrayid=1'>
	The disk in slot 1 should be a RAID 0 disk for the sles OS.
	</example>

	<example cmd='add os storage controller sles slot=2,3,4,5,6 raidlevel=6 hotspare=7,8 arrayid=2'>
	The disks in slots 2-6 on sles OS should be a RAID 6 with two
	hotspares associated with the array in slots 7 and 8.
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'os')

		self.command('add.storage.controller', self._argv + ['scope=os'])
		return self.rc
