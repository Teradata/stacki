# @copyright@ # Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import libvirt
import jinja2
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

class Hypervisor:

	"""
	Class to interface to a kvm hypervisor via
	the libvirt bindings. Can create and remove vm's,
	get the current state of guests, and manage
	storage pools or images.
	"""

	def __init__(self, host):
		libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)
		self.hypervisor = host
		self.kvm = self.connect()
		self.kvm_pool = """
			<pool type="dir">
			<name>{{ name }}</name>
			<target>
			<path>{{ dir }}</path>
			</target>
			</pool>
		"""
		self.kvm_volume = """
		<volume>
		<name>{{ volname }}</name>
		<allocation>0</allocation>
		<capacity unit="G">{{ size }}</capacity>
		<target>
			<path>{{ pooldir }}/{{ volname }}</path>
			<format type="qcow2"/>
		</target>
		</volume>
		"""

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
			hypervisor = libvirt.open(f'qemu+ssh://root@{self.hypervisor}/system')
		except libvirtError as msg:
			raise VmException(f'Failed to connect to hypervisor {self.hypervisor}:\n{msg}')
		return hypervisor

	def close(self):
		"""
		Close a connection to a hypervisor

		Raises a VmException if the hypervisor wasn't
		connected to or failed to close the connection
		"""

		if not self.kvm:
			raise VmException(f'Cannot find hypervisor connection to {self.hypervisor}')
		try:
			self.kvm.close()
		except libvirtError as msg:
			raise VmException(f'Failed to close hypervisor connection to {self.hypervisor}:\n{msg}')

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
			raise VmException(f'Failed to get list of VM domains on {self.hypervisor}:\n{msg}')

		for dom in domains:
			status = 'off'
			if dom.isActive():
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
			# Tell the hypervisor to add a new domain
			# using the provided libvirt config
			self.kvm.defineXML(dom_config)
		except libvirtError as msg:

			# If a vm is already defined do nothing
			# but raise an exception for other errors
			if 'already exists with' in str(msg):
				return
			raise VmException(f'Failed to define guest on hypervisor {self.hypervisor}:\n{msg}')

	def remove_domain(self, guest_name):
		"""
		Remove a guest domain with the given name
		from its hypervisor

		Raises a VmException if the VM could not be
		removed
		"""

		try:
			dom = self.kvm.lookupByName(guest_name)

			# Remove the domain definition from the hypervisor
			# Will remain to be defined until it is turned
			# off
			dom.undefine()
		except libvirtError as msg:
			raise VmException(f'Failed to undefine VM {guest_name} on hypervisor {self.hypervisor}:\n{str(msg)}')

	def start_domain(self, guest_name):
		"""
		Start a domain on a hypervisor

		Raises a VmException if the VM
		failed to be started
		"""
		try:
			dom = self.kvm.lookupByName(guest_name)

			# Start running a defined
			# domain on a hypervisor
			dom.create()
		except libvirtError as msg:
			raise VmException(f'Failed to start VM {guest_name} on hypervisor {self.hypervisor}:\n{msg}')

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
			raise VmException(f'Failed to stop VM {guest_name} on hypervisor {self.hypervisor}:\n{msg}')

	def add_pool(self, poolname, pooldir):
		"""
		Define a new kvm storage pool
		with the given pool directory and name

		Returns the pool name if the pool was created
		Skips pools already created with the same name

		If the pool was created, the pool is set to
		autostart, meaning the pool is not destroyed
		upon hypervisor reboot

		Raises a VmException if the pool failed
		to be created
		"""

		# Need to ensure the directory exists on the kvm host
		_exec(f'ssh {self.hypervisor} "mkdir -p {pooldir}"', shlexsplit = True)
		pool_exists = None
		try:
			pool_template = jinja2.Template(self.kvm_pool)
			pool_vars = {'name': poolname, 'dir': pooldir}
			pool_exists = self.kvm.storagePoolLookupByName(poolname)
			if pool_exists:
				return

		# Libvirt will raise an error if a pool doesn't exist
		# with the given name, so continue with making a new pool
		# if this is the case
		except libvirtError:
			pass

		try:
			# Render the template to create the pool
			# According to the libvirt docs, zero
			# always needs to be passed in
			pool = self.kvm.storagePoolDefineXML(pool_template.render(pool_vars), 0)
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
			raise VmException(f'Failed to delete pool {poolname} on hypervisor {self.hypervisor}:\n{msg}')

	def add_volume(self, volname, pooldir, poolname, size):
		"""
		Add a new storage volume to a pool

		Raises a VmException if the volume couldn't be added
		"""

		error_msg = f'Failed to create volume {volname} on hypervisor {self.hypervisor}'
		template = jinja2.Template(self.kvm_volume)

		try:
			pool = self.kvm.storagePoolLookupByName(poolname)
		except libvirtError as msg:
			raise VmException(f'{error_msg}:\n{msg}')

		# If there is a volume in the same pool matching the name
		# parameter assume that this means the volume is already created
		# so if we get a libvirt error, the volume has not been created
		try:
			vol = pool.storageVolLookupByName(volname)
			return
		except libvirtError:
			pass
		try:
			volume_vars = {'volname': volname, 'size': size, 'dir': pooldir }

			# Render the volume template
			# According to the libvirt docs, zero
			# always needs to be passed in
			pool.createXML(template.render(volume_vars), 0)
		except libvirtError as msg:
			raise VmException(f'{error_msg}:\n{msg}')

	def remove_volume(self, poolname, volname):
		"""
		Remove a storage volume from a pool
		and the underlying disk file

		Raises a VmException if the volume
		failed to be deleted
		"""

		try:
			pool = self.kvm.storagePoolLookupByName(poolname)
			vol = pool.storageVolLookupByName(volname)
			vol.delete()
		except libvirtError as msg:
			raise VmException(f'Failed to delete volume {volname} on hypervisor {self.hypervisor}:\n{msg}')

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
			raise VmException(f'Could not autostart {vm} on {self.hypervisor}:\n{str(msg)}')
