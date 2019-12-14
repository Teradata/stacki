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
	Set the virtual machine the disk is assigned to.

	<arg type='string' name='host' repeat='1'>
	The current virtual machine the disk is assigned to.
	</arg>

	<param type='string' name='disk' optional='0'>
	The disk to assign to a new host.
	</param>

	<param type='string' name='newhost' optional='0'>
	The hostname of the virtual machine host to assign
	the disk to.
	</param>

	<example cmd='set vm storage host virtual-backend-0-2 disk=sda newhost=virtual-backend-0-1'>
	Assign disk sda from virtual-backend-0-2 to virtual-backend-0-1 if a disk with name
	sda is not already defined.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getSingleHost(args)
		hosts = self.valid_vm_args(args)

		# There is only one host in the list
		# returned by valid_vm_args
		vm = hosts[0]
		disk_name, new_vm = self.fillParams([
			('disk', '', True),
			('newhost', '', True)
		])

		if not self.valid_vm(new_vm):
			raise ParamError(self, 'newhost', f'{new_vm} is not a valid virtual host')

		vm_id = self.vm_id_by_name(vm)
		new_vm_id = self.vm_id_by_name(new_vm)
		vm_disks = self.call(f'list.vm.storage', [vm, new_vm])

		disk_names = [ disk['Name'] for disk in vm_disks if disk['Virtual Machine'] == vm ]
		new_vm_disks = [ disk['Name'] for disk in vm_disks if disk['Virtual Machine'] == new_vm ]

		# Check if the disk name parameter
		# is a defined disk on the current host
		if disk_name not in disk_names:
			raise ParamError(self, 'disk', f'Disk {disk_name} not found defined for {vm}')

		# Check the new host doesn't have
		# a disk with the same name
		if disk_name in new_vm_disks:
			raise ParamError(self, 'disk', f'Disk {disk_name} found already defined on {new_vm}')

		self.db.execute(
			"""
			UPDATE virtual_machine_disks SET virtual_machine_id=%s
			WHERE virtual_machine_disks.disk_name = %s
			AND virtual_machine_disks.virtual_machine_id = %s
			""",
			(new_vm_id, disk_name, vm_id)
		)
