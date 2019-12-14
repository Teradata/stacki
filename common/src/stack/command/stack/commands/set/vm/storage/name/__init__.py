# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import CommandError, ParamError

class Command(stack.commands.set.vm.command):
	"""
	Set the disk device name of a vm.

	<arg type='string' name='host' repeat='1'>
	The virtual machine host the disk is assigned to.
	</arg>

	<param type='string' name='name' optional='0'>
	The new name of the disk device.
	</param>

	<param type='string' name='backing' optional='0'>
	The name of the backing file for the disk.
	Can be an image file, a created disk, or a mountpoint.
	</param>

	<example cmd='set vm storage name virtual-machine-0-1 name=sdb backing=virtual-machine-0-1_disk1.qcow2'>
	Assign disk sdb to the backing virtual-machine-0-1_disk1.qcow2
	</example>
	"""

	def run(self, params, args):
		hosts = self.getSingleHost(args)
		hosts = self.valid_vm_args(args)
		backing, disk_name = self.fillParams([
			('backing', '', True),
			('name', '', True)
		])

		for vm in hosts:
			vm_id = self.vm_id_by_name(vm)
			vm_disks = [ disk for disk in self.call(f'list.vm.storage', [vm]) ]
			disk_names = [ disk['Name'] for disk in vm_disks ]
			disk_images = [ disk['Image Name'] for disk in vm_disks if disk['Image Name'] ]


			# A mountpoint won't be in the image list, so don't raise
			# an error if it's not there
			if backing not in disk_images and '/dev' not in backing:
				raise ParamError(self, 'backing', f'{backing} not found for {vm}, is the backing a defined disk for that host?')

			# No disks with the same device name
			if disk_name in disk_names:
				raise CommandError(self, f'Disk with name {disk_name} already exists for {vm}')

			# Handle mountpoints
			if '/dev' in backing:
				self.db.execute(
					"""
					UPDATE virtual_machine_disks SET disk_name=%s
					WHERE virtual_machine_disks.mount_disk = %s
					AND virtual_machine_disks.virtual_machine_id = %s
					""",
					(disk_name, backing, vm_id)
				)
			else:
				self.db.execute(
					"""
					UPDATE virtual_machine_disks SET disk_name=%s
					WHERE virtual_machine_disks.image_file_name = %s
					AND virtual_machine_disks.virtual_machine_id = %s
					""",
					(disk_name, backing, vm_id)
				)
