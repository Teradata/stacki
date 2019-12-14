# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import tarfile
from pathlib import Path
from stack.exception import CommandError, ArgRequired, ParamError

class Command(stack.commands.add.vm.Command):
	"""
	Add storage to a virtual machine.

	<arg type='string' name='host' optional='1'>
	The name of the virtual machine to add the new
	storage to
	</arg>

	<param type='string' name='storage_pool' optional='1'>
	The location of the storage pool where storage will be created
	or transfered
	</param>

	<param type='string' name='disks' optional='1'>
	A list of disks or single disk for a virtual machine. Can be an integer to
	create a new disk image for the virtual machine, a path to a compressed (tar or gzip)
	or uncompressed qcow2 or raw image, or a path to a disk device (such as /dev/sdb) to
	mount to a virtual machine.
	</param>

	<example cmd='add vm storage virtual-backend-0-1 storage_pool=/export/pool/stacki disks=200'>
	Add a new disk to virtual-backend-0-1 at the location of /export/pool/stacki
	(for created disks this will create a new pool with the name stacki if it doesn't exist)
	</example>

	<example cmd='add vm storage virtual-backend-0-1 storage_pool=/export/pool/stacki disks=/export/stacki.qcow2,/dev/sdb'>
	Add two new disks to virtual-backend-0-1: the first is a premade qcow2 image which will be the boot disk
	(order is from list of being added), the second is a disk that will be mounted to the VM as a mountpoint
	</example>

	"""

	def run(self, params, args):
		vm_host = self.getSingleHost(args)
		vm_host = self.valid_vm_args([vm_host])

		# Default naming scheme for newly made disk volumes
		# of $HOSTNAME_disk followed by an incrementing number
		# for each new disk
		vol_name = f'{vm_host[0]}_disk'
		dev_id = 0
		vol_id = 0
		disk_loc, disks = self.fillParams([
			('storage_pool', ''),
			('disks', '', True)
		])
		vm_disks = self.call('list.vm.storage', vm_host)
		disk_names = [ disk['Name'] for disk in vm_disks ]
		disk_names.sort()

		if disk_loc:
			disk_loc = f'{disk_loc}/{vm_host[0]}'

		# Get the name of all disks for the VM
		image_formats = ['.qcow2', '.raw']

		for disk in disks.split(','):
			image_archive = None
			disk_size = None
			mount_disk = None
			curr_images = [ disk['Image Name'] for disk in vm_disks if disk['Image Name'] and disk['Type'] == 'disk']

			# The calculated names of newly created disks
			vol_names = []

			# All the disks to be added into the database
			images = []

			disk_path = Path(disk)

			disk_name = f'sd{chr(ord("a") + dev_id)}'

			# Only want storage of type disk (i.e. created volumes) that match the default
			# naming scheme in order to determine the next disk name, ignoring custom names
			for name in curr_images:
				if vol_name in name:
					vol_names.append(name)

			# If the disk is a number it's a disk to be created
			# during vm definition
			if disk.isdigit():
				if not disk_loc:
					raise ParamError(self, 'storage_pool', 'needed for defined disks or images')
				disk_type = 'disk'
				disk_size = disk
				if vol_names:
					try:
						# Get the disk number in the volume name
						vol_file = vol_names[-1].replace(Path(vol_names[-1]).suffix, '')
						vol_id = int(vol_file.split(vol_name)[1]) + 1

					# Just increment the disk name number if we can't get the last created one
					except (IndexError, ValueError):
						vol_id += 1
				else:
					vol_id += 1
				disk_image = f'{vol_name}{vol_id}.qcow2'
				images.append(disk_image)

			# A path existing on the frontend is a compressed/uncompressed disk file
			# First check if it's a valid tar file
			elif disk_path.exists() and not disk_path.is_dir() and tarfile.is_tarfile(disk_path):
				if not disk_loc:
					raise ParamError(self, 'storage_pool', 'needed for defined disks or images')
				disk_type = 'image'
				image_archive = disk
				tar_disks = tarfile.open(disk_path)
				tar_images = tar_disks.getnames()
				tar_disks.close()

				# Assume the top level files of the
				# tar archive are all vm images
				for vm_image in tar_images:
					if Path(vm_image).suffix in image_formats:
						images.append(vm_image)
			elif disk_path.exists():
				disk_type = 'image'
				if not disk_loc:
					raise ParamError(self, 'storage_pool', 'needed for defined disks or images')

				# First test for a gzip archive and replace the suffix for
				# the uncompressed disk image name
				if '.gz' in disk_path.suffix:

					# Remove the archive extension
					image_name = disk_path.name.replace(disk_path.suffix, '')
					image_archive = str(disk_path)
					images.append(image_name)

				else:

					# Otherwise assume the disk is an uncompressed
					# image
					if disk_path.suffix in image_formats:
						images.append(disk)
					else:
						raise ParamError(self, 'Virtual Machine disk {disk} not a qcow2 or raw image')

			elif '/dev/' in disk:

				# Unlike the other types of storage, mountpoints do not require
				# a storage directory as it is just a mounted disk to a VM
				disk_type = 'mountpoint'
				mount_disk = disk
				images.append('')

			# For an archive containing multiple disk images
			# Create a new entry in the table for each one
			# Insert disks into the database
			for image in images:

				# Calculate the next device name (sda, sdb, sdc...etc)
				if disk_names:
					disk_name = f'sd{chr(ord(disk_names[-1][-1]) + 1 + dev_id)}'
				self.db.execute("""
					INSERT INTO virtual_machine_disks
					(
						virtual_machine_id,
						disk_name,
						disk_location,
						disk_type,
						disk_size,
						image_file_name,
						image_archive_name,
						mount_disk
					)
					VALUES (
						(select virtual_machines.id from virtual_machines inner join nodes on node_id=nodes.id where name=%s),
						%s, %s, %s, %s, %s, %s, %s
					)
				""", (vm_host, disk_name, disk_loc, disk_type, disk_size, image, image_archive, mount_disk))
				dev_id += 1
