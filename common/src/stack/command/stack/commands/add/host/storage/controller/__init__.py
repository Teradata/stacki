# @copyright@
import stack.commands


class Command(stack.commands.add.command):
	"""
	Add a storage controller configuration for a host.

	<param type='int' name='adapter' optional='1'>
	Adapter address.
	</param>

	<param type='int' name='enclosure' optional='1'>
	Enclosure address.
	</param>

	<param type='int' name='slot'>
	Slot address(es). This can be a comma-separated list meaning all disks
	in the specified slots will be associated with the same array
	</param>

	<param type='int' name='raidlevel'>
	RAID level. Raid 0, 1, 5, 6 and 10 are currently supported.
	</param>

	<param type='int' name='hotspare' optional='1'>
	Slot address(es) of the hotspares associated with this array id. This
	can be a comma-separated list (like the 'slot' parameter). If the
	'arrayid' is 'global', then the specified slots are global hotspares.
	</param>

	<param type='string' name='arrayid'>
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

	<example cmd='add host storage controller backend-0-0 slot=1 raidlevel=0 arrayid=1'>
	The disk in slot 1 on backend-0-0 should be a RAID 0 disk, for the host 'backend'
	</example>

	<example cmd='add host storage controller backend-0-0 slot=2,3,4,5,6 raidlevel=6 hotspare=7,8 arrayid=2'>
	The disks in slots 2-6 on backend-0-0 should be a RAID 6 with two
	hotspares associated with the array in slots 7 and 8, for the host 'backend-0-0'
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('add.storage.controller', self._argv + [ 'scope=host' ]))
		return self.rc
