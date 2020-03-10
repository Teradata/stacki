# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import shlex
from stack.kvm import Hypervisor
from stack.kvm import VmException
from stack.argument_processors.vm import VmArgumentProcessor
from stack.util import _exec
from pathlib import Path
from contextlib import ExitStack

class Plugin(stack.commands.Plugin, VmArgumentProcessor):

	def provides(self):
		return 'storage'

	def requires(self):
		return ['hypervisor']

	def precedes(self):
		return ['config']

	def pack_ssh_key(self, host, hypervisor, disk):
		"""
		Packs the frontend's ssh key into the authorized keys
		of a given disk image, assumes there is a /root/.ssh folder
		on the target disk

		Returns a list containing any errors encountered
		"""

		key_dir = Path(f'/tmp/{host}_keys')

		with ExitStack() as cleanup:

			disk_name = Path(disk["Image Name"]).name

			# Create the temp key directory
			# on the remote host
			create_key_dir = _exec(f'ssh {hypervisor} "mkdir -p {key_dir}"', shlexsplit=True)
			disk_loc = Path(f'{disk["Location"]}/{disk_name}')

			# Ensure the temp key directory is
			# removed on the remote host
			remove_key_dir = shlex.split(f'ssh {hypervisor} "rm -r {key_dir}"')
			cleanup.callback(_exec, remove_key_dir)

			if create_key_dir.returncode != 0:
				return create_key_dir.stderr
			copy_key = _exec(f'scp /root/.ssh/id_rsa.pub {hypervisor}:{key_dir}/frontend_key', shlexsplit=True)
			if copy_key.returncode != 0:
				return copy_key.stderr

			# Get the existing authorized keys file
			# if it doesn't exist that's fine
			existing_keys = _exec(
				f'ssh {hypervisor} "virt-copy-out -a {disk_loc} /root/.ssh/authorized_keys {key_dir}"',
				shlexsplit=True
			)

			# Add the frontend's public key
			# to the authorized_keys file
			add_key = _exec(
				f'ssh {hypervisor} "cat {key_dir}/frontend_key >> {key_dir}/authorized_keys"',
				shlexsplit=True
			)
			if add_key.returncode != 0:
				return add_key.stderr

			# Put the key back into
			# the vm's disk image
			pack_image = _exec(
				f'ssh {hypervisor} "virt-copy-in -a {disk_loc} {key_dir}/authorized_keys /root/.ssh/"',
				shlexsplit=True
			)
			if pack_image.returncode != 0:
				return pack_image.stderr

	def copy_remote_file(self, file_path, dest_path, dest_host):
		"""
		Transfer over a file to a given host at a specified location.
		If the file already exists at the given location, it will not be
		overwritten.

		Returns a string containing any errors that occurred while transferring
		"""

		if not Path(file_path).is_file():
			return f'File {file_path} not found to transfer'

		transfer_file = Path(file_path)
		dest = Path(dest_path)

		# Path to transferred file location
		copy_file_path = Path(f'{dest}/{transfer_file.name}')

		# Create the path on the host
		create_dest = _exec(f'ssh {dest_host} "mkdir -p {dest}"', shlexsplit=True)
		if create_dest.returncode != 0:
			return f'Could not create file folder {dest} on {dest_host}:\n{create_dest.stderr}'

		# Check if the file already exists at the given location
		file_present = _exec(f'ssh {dest_host} "ls {copy_file_path}"', shlexsplit=True)
		if file_present.returncode == 0:
			return

		# Transfer the file
		copy_file = _exec(f'scp {transfer_file} {dest_host}:{dest}', shlexsplit=True)
		if copy_file.returncode != 0:
			return f'Failed to transfer file {transfer_file} to {dest_host} at {copy_file_path}:\n{copy_file.stderr}'

	def remove_remote_file(self, remove_file, host):
		"""
		Remove a file on the specified host
		at the given path

		Return a string if an error occurred
		"""

		file_path = Path(remove_file)
		file_present = _exec(f'ssh {host} "ls {file_path}"', shlexsplit=True)
		if file_present.returncode != 0:
			return f'Could not find file {file_path.name} on {host}'
		rm_file_out = _exec(f'ssh {host} "rm {file_path}"', shlexsplit=True)
		if rm_file_out.returncode != 0:
			return f'Failed to remove file {file_path.name}:{rm_file_out.stderr}'

	def remove_empty_dir(self, host, dir_loc):
		"""
		Remove a directory at a given host if it contains no files
		(assuming they aren't hidden)

		Return a string if an error occurred
		"""

		dir_empty = _exec(f'ssh {host} "ls {dir_loc}"', shlexsplit=True)
		if dir_empty.returncode != 0:
			return f'Failed to find {dir_loc} on {host}'
		if dir_empty.stdout != '':
			return f'Found files present in {dir_loc} on {host}'
		remove_dir = _exec(f'ssh {host} "rm -r {dir_loc}"', shlexsplit=True)
		if remove_dir.returncode != 0:
			return f'Failed to remove directory {dir_loc} on {host}:\n{remove_dir.stderr}'

	def add_disk(self, host, hypervisor, disk, sync_ssh, debug):
		"""
		Add a given disk to a hypervisor.

		Returns any errors that occurred as a string.
		"""

		disk_type = disk['Type']
		image_loc = Path(disk['Location'])
		add_errors = []

		# Create a disk at the specified location
		if disk_type == 'disk':
			pool = image_loc.name
			try:
				with Hypervisor(hypervisor) as conn:
					add_pool = conn.add_pool(image_loc.name, image_loc)
					if not add_pool and debug:
						self.owner.notify(f'Pool {pool} already created, skipping')
					vol_name = disk['Image Name']
					if debug:
						self.owner.notify(f'Create storage volume {vol_name} with size {disk["Size"]}')

					# Add the disk to the hypervisor
					conn.add_volume(vol_name, image_loc, pool, disk['Size'])
			except VmException as error:
				add_errors.append(str(error))

		# copy disk images over if
		# they aren't already present
		elif disk_type == 'image':
			image_name = Path(disk['Image Name']).name

			copy_file = disk['Image Name']
			if debug:
				self.owner.notify(f'Transferring file {copy_file}')

			# Copy the image
			output = self.copy_remote_file(copy_file, image_loc, hypervisor)
			if output:
				add_errors.append(output)

			# Add the frontend's ssh key, assume the image contains an OS
			if sync_ssh:
				if debug:
					self.owner.notify(f'Adding frontend ssh key to {image_name}')
				pack_ssh_errors = self.pack_ssh_key(host, hypervisor, disk)
				if pack_ssh_errors and debug:
					add_errors.append(f'Failed to pack frontend ssh key: {pack_ssh_errors}')
		return add_errors

	def remove_disk(self, hypervisor, disk, debug):
		"""
		Remove the given disk volume or image from the
		hypervisor host

		Return any errors that occurred as a string.
		"""

		disk_type = disk['Type']
		image_loc = Path(disk['Location'])
		remove_errors = []

		if disk_type == 'disk':
			vol_name = disk['Image Name']
			try:
				with Hypervisor(hypervisor) as conn:
					if debug:
						self.owner.notify(f'Removing disk {vol_name}')

					# Remove a volume from its pool
					# which is determined by the last
					# part of the path of the disk location
					conn.remove_volume(image_loc.name, vol_name)
			except VmException as error:
				remove_errors.append(str(error))

		# Remove an image file on the hypervisor
		elif disk_type == 'image':
			image_name = Path(disk['Image Name']).name
			if debug:
				self.owner.notify(f'Removing image {image_name}')
			output = self.remove_remote_file(f'{image_loc}/{image_name}', hypervisor)
			if output:
				remove_errors.append(output)
		return remove_errors

	def remove_pool(self, pool_name, hypervisor, debug):
		"""
		Remove a given pool name on a provided hypervisor host
		"""

		remove_errors = []
		try:
			with Hypervisor(hypervisor) as conn:
				if debug:
					self.owner.notify(f'Removing storage pool {pool_name}')
				conn.remove_pool(pool_name)
		except VmException as msg:
			remove_errors.append(str(msg))
		return remove_errors

	def remove_storage_dir(self, host, hypervisor, disks, debug):
		"""
		Remove the storage directory for each disk if its a directory
		containing the VM hostname (which we assume is owned by the VM)
		"""

		host_dir = ''
		remove_errors = []
		for disk in disks:
			disk_path = Path(disk['Location'])
			if disk_path.name == host:
				host_dir = disk['Location']
				if debug:
					self.owner.notify(f'Removing storage directory for {host}')
				remove_dir = self.remove_empty_dir(hypervisor, host_dir)
				if remove_dir:
					remove_errors.append(remove_dir)

				# After removing the folder containing the VM
				# name we are done
				break
		return remove_errors

	def run(self, args):
		hosts, host_disks, debug, sync_ssh, force, hypervisor = args
		config_errors = []
		self.owner.notify('Sync VM Storage')
		for host, disks in host_disks.items():
			has_pool = False
			del_disks = {}
			add_disks = []
			hypervisor = hosts[host]['hypervisor']
			for disk in disks:
				if disk['Type'] == 'disk':
					has_pool = True

				# Remove any disks assigned to a VM marked for deletion
				if self.owner.str2bool(disk['Pending Deletion']):
					remove_output = self.remove_disk(hypervisor, disk, debug)
					del_disks[disk['Name']] = disk
					config_errors.extend(remove_output)

				# Otherwise try to add it
				else:
					add_output = self.add_disk(host, hypervisor, disk, sync_ssh, debug)
					add_disks.append(disk)
					config_errors.extend(add_output)

			# If all the current disks have been deleted
			# and no new ones added, remove the storage pool
			# and directory as its empty now
			if list(del_disks.values()) == disks and not add_disks:
				if has_pool:
					pool_errors = self.remove_pool(host, hypervisor, debug)
					config_errors.extend(pool_errors)

				# Remove the actual storage directory
				dir_errors = self.remove_storage_dir(host, hypervisor, disks, debug)
				config_errors.extend(dir_errors)

		return config_errors
