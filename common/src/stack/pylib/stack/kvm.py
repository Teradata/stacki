# @copyright@ # Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import libvirt
import tarfile
from libvirt import libvirtError
from stack.util import _exec
from pathlib import Path

# Libvirt has a weird quirk where it prints
# error messages even if they are handled via
# exceptions, code taken from:
# stackoverflow.com/questions/45541725/avoiding-console-prints-by-libvirt-qemu-python-apis
def libvirt_callback(userdata, err):
	pass

class VmException(Exception):
	pass

class VM:

	"""
	Class to interface to a kvm hypervisor via
	the libvirt bindings. Can create and remove vm's,
	get the current state of guests, and manage
	storage pools or images.
	"""

	def __init__(self, host):
		libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)
		self.hostname = host
		self.kvm = self.connect()

	def connect(self):
		"""
		Establish a connection to the hypervisor
		and return the object.

		Raises a VmException if connection to
		the hypervisor failed
		"""

		# We assume the frontend
		# has ssh access to the
		# hypervisor
		try:
			hypervisor = libvirt.open(f'qemu+ssh://root@{self.hostname}/system')
		except libvirtError:
			raise VmException(f'Failed to connect to hypervisor {self.hostname}')
		return hypervisor

	def close(self):
		"""
		Close a connection to a hypervisor

		Raises a VmException if the hypervisor wasn't
		connected to or failed to close the connection
		"""

		if not self.kvm:
			raise VmException(f'Cannot find hypervisor connection to {self.hostname}')
		try:
			self.kvm.close()
		except libvirtError:
			raise VmException(f'Failed to close hypervisor connection to {self.hostname}')

	def guests(self):
		"""
		Return a dict of all guests defined on the
		current hypervisor along with their current
		status.

		Raises a VmException if the guest list could
		not be retrieved
		"""

		vm_guests = {}

		try:
			domains = self.kvm.listAllDomains()

			except libvirtError as msg:
				raise VmException(f'Failed to get list of VM domains on {self.hostname}:\n{msg}')

		for dom in domains:
			status = 'off'
			if dom.isActive() == True:
				status = 'on'
			vm_guests[dom.name()] = status

		return vm_guests

	def add_domain(self, dom_config):
		"""
		Define a new guest in the hypervisor

		Raises a VmException if the failed to
		be added
		"""

		try:
			self.kvm.defineXML(dom_config)
		except libvirtError as msg:

			# If a vm is already defined do nothing
			# but raise an exception for other errors
			if 'already exists with' in str(msg):
				return
			raise VmException(f'Failed to define guest on hypervisor {self.hostname}:\n{msg}')

	def remove_domain(self, guest_name):
		"""
		Remove a guest domain with the given name

		Raises a VmException if the VM could not be
		removed
		"""

		try:
			dom = self.kvm.lookupByName(guest_name)
			dom.undefine()
		except libvirtError as msg:
			raise VmException(f'Failed to undefine VM {guest_name} on hypervisor {self.hostname}:\n{str(msg)}')

	def start_domain(self, guest_name):
		"""
		Start a domain on a hypervisor

		Raises a VmException if the VM
		failed to be started
		"""
		try:
			dom = self.kvm.lookupByName(guest_name)
			dom.create()
		except libvirtError as msg:
			raise VmException(f'Failed to start VM {guest_name} on hypervisor {self.hostname}:\n{msg}')

	def stop_domain(self, guest_name):
		"""
		Stop a domain on a hypervisor

		Raises a VmException if the VM could
		not be stopped
		"""

		try:
			dom = self.kvm.lookupByName(guest_name)

                        # This sounds scary but just stops the vm
			dom.destroy()
		except libvirtError as msg:
			raise VmException(f'Failed to stop VM {guest_name} on hypervisor {self.hostname}:\n{msg}')

	def add_pool(self, poolname, pooldir):
		"""
		Define a new kvm storage pool
		with the given pool directory and name

		Returns empty string if the pool exists
		and the pool name if the pool was created

		Raises a VmException if the pool failed
		to be created
		"""

		poolxml = f"""<pool type="dir">
	<name>{poolname}</name>
	<target>
		<path>{pooldir}</path>
	</target>
	</pool>"""

		# Need to ensure the directory exists on the kvm host
		self.do_remote_command('root', [ f'mkdir -p {pooldir}' ])
		try:
			pools = self.kvm.listAllStoragePools(0)
			pool_exists = self.kvm.storagePoolLookupByName(poolname)
			if pool_exists:
				return
			pool = self.kvm.storagePoolDefineXML(poolxml, 0)
			pool.create()
			pool.setAutostart(1)
		except libvirtError as msg:
			raise VmException(f'Failed to create storage pool {pooldir}:\n{msg}')
		return poolname

	def remove_pool(self, poolname):
		"""
		Remove a storage pool

		Raises a VmException if the poolname could not be deleted
		"""

		try:
			pool = self.kvm.storagePoolLookupByName(poolname)
			pool.undefine()
		except libvirtError as msg:
			raise VmException(f'Failed to delete pool {poolname} on hypervisor {self.hostname}:\n{msg}')

	def add_volume(self, volname, pooldir, poolname, size):
		"""
		Add a new storage volume to a pool

		Raises a VmException if the volume couldn't be added
		"""

		volxml = f"""<volume>
	<name>{volname}</name>
	<allocation>0</allocation>
	<capacity unit="G">{size}</capacity>
	<target>
		<path>{pooldir}/{volname}</path>
		<format type="qcow2"/>
	</target>
	</volume>"""

		error_msg = f'Failed to create volume {volname} on hypervisor {self.hostname}'

		try:
			pool = self.kvm.storagePoolLookupByName(poolname)
		except libvirtError as msg:
			raise VmException(f'{error_msg}:\n{msg}')

			# If there is a volume in the same pool matching the name
			# parameter assume that this means the volume is already created
		try:
			vol = pool.storageVolLookupByName(volname)
			return
		except libvirtError:
			pass
		try:
			pool.createXML(volxml, 0)
		except libvirtError as msg:
			raise VmException(f'{error_msg}:\n{msg}')

	def remove_volume(self, poolname, volname):
		"""
		Remove a storage volume from a pool

		Raises a VmException if the volume
		failed to be deleted
		"""

		try:
			pool = self.kvm.storagePoolLookupByName(poolname)
			vol = pool.storageVolLookupByName(volname)
			vol.delete()
		except libvirtError as msg:
			raise VmException(f'Failed to delete volume {volname} on hypervisor {self.hostname}:\n{msg}')

	def copy_image(self, image_path, dest_path, image_name = ''):
		if Path(image_path).is_file():
			image = Path(image_path)
			dest = Path(dest_path)
			curr_image = Path(f'{dest}/{image_name}')
			copy_image = f'{dest}/{image.name}'

			# Create the path on the host
			create_dest = _exec(f'ssh {self.hostname} "mkdir -p {dest}"', shlexsplit=True)
			if create_dest.returncode != 0:
				raise VmException(f'Could not create image folder {dest} on {self.hostname}:\n{create_dest.stderr}')

			# Check if the image already exists at the given location
			if image_name:
				image_present = _exec(f'ssh {self.hostname} "ls {curr_image}"', shlexsplit=True)
				if image_present.returncode == 0:
					return

			# Transfer the image
			transfer_image = _exec(f'scp {image} {self.hostname}:{dest}', shlexsplit=True)
			if transfer_image.returncode != 0:
				raise VmException(f'Failed to transfer image {image} to {self.hostname} at {image}:\n{transfer_image.stderr}')

			# Use tar to uncompress the image if its in a tarfile
			if tarfile.is_tarfile(image_path):
				untar = _exec(f'ssh {self.hostname} "tar -xvf {copy_image} -C {dest} && rm {copy_image}"', shlexsplit=True)
				if untar.returncode != 0:
					raise VmException(f'Failed to unpack vm image {image} on {self.hostname}:\n{untar.stderr}')

			# Otherwise use gunzip if its compressed using gzip
			elif image.name.endswith('gz'):
				unzip = _exec(f'ssh {self.hostname} "gunzip {copy_image}"', shlexsplit=True)
				if unzip.returncode != 0:
					raise VmException(f'Failed to unpack vm image {image} on {self.hostname}:\n{unzip.stderr}')
		else:
			raise VmException(f'Disk image {image_path} not found to transfer')

	def remove_image(self, image_path):
		"""
		Remove an image at the given path

		Raises a VmException if the image failed
		to be removed
		"""

		image = Path(image_path)
		image_present = _exec(f'ssh {self.hostname} "ls {image}"', shlexsplit=True)
		if image_present.returncode != 0:
			raise VmException(f'Could not find image file {image.name} on {self.hostname}')
		rm_image = _exec(f'ssh {self.hostname} "rm {image}"', shlexsplit=True)
		if rm_image.returncode != 0:
			raise VmException(f'Failed to remove image {image.name}:{rm_image.stderr}')

	def autostart(self, vm, is_autostart = False):
		"""
		Set a virtual machine to start upon boot
		of the hypervisor

		Raises a VmException if the VM couldn't be set to
		autostart
		"""

		try:
			dom = self.kvm.lookupByName(vm)
			if is_autostart:
				dom.setAutostart(1)
			else:
				dom.setAutostart(0)
		except libvirtError as msg:
			raise VmException(f'Could not autostart {vm} on {self.hostname}:\nmsg')
