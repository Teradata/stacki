# @copyright@ # Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import libvirt
import jinja2
import tarfile
import math
from libvirt import libvirtError
from stack.util import _exec
from pathlib import Path
from collections import defaultdict

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
	the libvirt api bindings. Can create and remove vm's,
	get the current state of guests, and manage
	storage pools/volumes or pre-made images.
	"""

	# The file path for where to place
	# VM config files on the hypervisor
	conf_loc = '/etc/libvirt/qemu/'

	def __init__(self, host):
		libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)
		self.hypervisor = host
		self.kvm = None

		# Template for defining storage pools in libvirt
		self.kvm_pool = """
			<pool type="dir">
			<name>{{ name }}</name>
			<target>
			<path>{{ dir }}</path>
			</target>
			</pool>
		"""

		# Template for defining storage volumes in libvirt
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

	# Connect automatically and close the connection when
	# calling the hypervisor class as a context manager
	def __enter__(self, *args):
		self.kvm = self.connect()
		return self

	def __exit__(self, *args):
		self.close()
		return self

	def connect(self):
		"""
		Establish a connection to the hypervisor
		and return the object.

		Raises a VmException if connection to
		the hypervisor failed
		"""

		# We assume the frontend
		# has ssh access to the
		# hypervisor as root
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

			# Get the domain object
			dom = self.kvm.lookupByName(guest_name)

			# create() starts running a defined
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

			# destroy() sounds scary but just stops the vm
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

			# Set the pool to be inactive, then undefine it
			pool.destroy()
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

	def pool_info(self, filter_pool=''):
		"""
		Return the storage pool information
		of the hypervisor.

		Optionally takes a filter_pool param for
		returning info on a specific pool, otherwise
		returns all pool info on the hypervisor

		Returns an empty dict if filter_pool is set
		to a pool that isn't found or a dict of pool
		information if it is

		Raises a VmException if the the pool info
		couldn't be found
		"""

		pool_val = defaultdict(dict)
		try:
			if filter_pool:
				pools = [pool for pool in self.kvm.listAllStoragePools(0) if pool.name() == filter_pool]
			else:
				pools = self.kvm.listAllStoragePools(0)
			for pool in pools:
				p_name = pool.name()
				info = pool.info()

				# Libvirt returns storage pool sizes in KB
				# convert to GB
				pool_val[p_name]['capacity'] = f'{round(info[1] / math.pow(2, 30), 2)} GB'
				pool_val[p_name]['allocated'] = f'{round(info[2] / math.pow(2, 30), 2)} GB'
				pool_val[p_name]['available'] = f'{round(info[3] / math.pow(2, 30), 2)} GB'
				pool_val[p_name]['is_active'] = bool(pool.isActive())
			return pool_val
		except libvirtError as msg:
			raise VmException(f'Failed to get pool info on {self.hypervisor}:\n{str(msg)}')
