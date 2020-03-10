# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.util import _exec
from pathlib import Path
from stack.exception import CommandError, ArgRequired, ParamError

class Command(stack.commands.add.vm.Command):
	"""
	Add storage to a virtual machine.

	<arg type='string' name='host' optional='1'>
	The name of the virtual machine to add new storage to
	</arg>

	<param type='string' name='storage_pool' optional='1'>
	The location of the storage pool where storage will be created
	or transferred to
	</param>

	<param type='string' name='disks' optional='1'>
	A list of disks or single disk for a virtual machine. Can be an integer to
	create a new disk image for the virtual machine, a path to a qcow2 or raw image,
	or a path to a disk device (such as /dev/sdb) to mount to a virtual machine .
	</param>

	<example cmd='add vm storage virtual-backend-0-1 storage_pool=/export/pool/stacki disks=200'>
	Add a new disk to virtual-backend-0-1 at the location of /export/pool/stacki/virtual-backend-0-1
	Disks are always sorted into folders by virtual machine host name
	</example>

	<example cmd='add vm storage virtual-backend-0-1 storage_pool=/export/pool/stacki disks=/export/stacki.qcow2,/dev/sdb'>
	Add two new disks to virtual-backend-0-1: the first is a premade qcow2 image which will be the boot disk
	(order is from list of being added), the second is a disk that will be mounted to the VM as a mountpoint
	</example>

	"""
	def valid_image(self, file_path):
		"""
		Use qemu-img to check the VM image
		we are given is valid.
		"""

		# Valid disk formats
		img_formats = ['qcow2', 'raw']

		# Get the image info as json
		output = _exec(f'qemu-img info --output=json {file_path}', shlexsplit=True)
		if output.returncode != 0:
			return False
		img_info = json.loads(output.stdout)
		image_ext = file_path.suffix.replace('.', '')

		# Check qemu-img info and file extension
		# as it classifies any file as raw
		if img_info['format'] in img_formats and image_ext in img_formats:
			return True
		return False

	def run(self, params, args):
		vm_host = self.getSingleHost(args)
		vm_host = self.valid_vm_args([vm_host])

		# Default naming scheme for newly made disk volumes
		# is $HOSTNAME_disk followed by an incrementing number
		# for each new disk
		vol_name = f'{vm_host[0]}_disk'
		vol_id = 0
		disk_name = 'sda'
		disk_loc, disks = self.fillParams([
			('storage_pool', ''),
			('disks', '', True)
		])
		if disk_loc:
			disk_loc = Path(f'{disk_loc}/{vm_host[0]}')

		for disk in disks.split(','):
			image = ''
			disk_size = None
			mount_disk = None

			# Get the current disks
			vm_disks = self.call('list.vm.storage', vm_host)

			# Used for calculating the device name
			disk_names = [ disk['Name'] for disk in vm_disks ]

			# Used for disks created on the hypervisor
			vol_names = [ disk['Image Name'] for disk in vm_disks if disk['Image Name'] and disk['Type'] == 'disk']
			disk_path = Path(disk)

			# If the disk is a number it's a disk to be created
			# during vm definition
			if disk.isdigit():
				if not disk_loc:
					raise ParamError(self, 'storage_pool', 'needed for defined disks or images')
				disk_type = 'disk'
				disk_size = disk
				if vol_names:

					# Get the next disk name but only consider other disk type images
					vol_file = vol_names[-1].replace(Path(vol_names[-1]).suffix, '')
					vol_id = int(vol_file.split(vol_name)[1]) + 1
				else:
					vol_id += 1
				image = f'{vol_name}{vol_id}.qcow2'

			elif disk.startswith('/dev/'):

				# Unlike the other types of storage, mountpoints do not require
				# a storage directory as it is just a mounted disk to a VM
				disk_type = 'mountpoint'
				mount_disk = disk

			else:
				if not disk_loc:
					raise ParamError(self, 'storage_pool', 'needed for defined disks or images')

				# Otherwise assume the disk is an premade image
				disk_type = 'image'
				image = str(disk_path)
				if not self.valid_image(disk_path):
					raise ParamError(self, 'disks', f'Virtual Machine disk {disk} not found or not a qcow2 or raw image')

			# Calculate the next device name (sdb, sdc, sdd...etc)
			if disk_names:
				disk_name = f'sd{chr(ord(disk_names[-1][-1]) + 1)}'

			# Insert disks into the database
			self.db.execute("""
			INSERT INTO virtual_machine_disks
				(
					virtual_machine_id,
					disk_name,
					disk_location,
					disk_type,
					disk_size,
					image_file_name,
					mount_disk
				)
				VALUES (
					(select virtual_machines.id from virtual_machines inner join nodes on node_id=nodes.id where name=%s),
					%s, %s, %s, %s, %s, %s
				)
			""", (vm_host, disk_name, str(disk_loc), disk_type, disk_size, image, mount_disk))
