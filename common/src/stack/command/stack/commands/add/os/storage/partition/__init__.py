# @copyright@
import stack.commands


class Command(stack.commands.add.command):
	"""
	Add storage partition configuration for an os.

	<arg type='string' name='os' optional='0'>
	os name
	</arg>

	<param type='string' name='device' optional='0'>
	Disk device on which we are creating partitions
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint to create
	</param>

	<param type='int' name='size' optional='0'>
	Size of the partition.
	Set as 0 to get maximum remaining size .
	</param>

	<param type='string' name='type' optional='1'>
	Type of partition E.g: ext4, ext3, xfs, raid, etc.
	</param>

	<param type='string' name='options' optional='0'>
	Options that need to be supplied while adding partitions.
	</param>

	<param type='int' name='partid' optional='1'>
	The relative partition id for this partition. Partitions will be
	created in ascending partition id order.
	If no partid is provided the decision will determined by the installer.
	</param>

	<example cmd='add os storage partition redhat device=sda mountpoint=/var
		size=50 type=ext4'>
	Creates a ext4 partition on device sda with mountpoints /var.
	for the os 'redhat'
	</example>

	<example cmd='add os storage partition redhat device=sda partid=1
	    mountpoint=/ fstype=xfs' size=10000>
	Adds the partition sda1 to be formatted as a 10 GB xfs and mounted to '/'
	for the os 'redhat'
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('add.storage.partition', self._argv + ['scope=os']))
		return self.rc
