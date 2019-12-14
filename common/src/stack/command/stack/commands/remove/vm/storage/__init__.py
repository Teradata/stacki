# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
import stack.commands
from stack.exception import ParamError

class Command(stack.commands.remove.vm.Command):
	"""
	Mark a virtual machine's disk for deletion.

	<arg type='string' name='host' optional='1'>
	A single hostname with to remove a disk from.
	</arg>

	<param type='string' name='disk' optional='1'>
	The name of the disk to remove from the virtual machine.
	</param>

	<example cmd='remove vm storage virtual-backend-0-1 disk=sda'>
	Mark disk sda for deletion from virtual-backend-0-1. Upon running
	sync vm, the disk will be deleted on the hypervisor and removed from
	the frontend.
	</example>
	"""

	def run(self, params, args):

		# We only want a single host argument
		host = self.getSingleHost(args)
		host = self.valid_vm_args([host])

		# Get the disk names for the host
		host_disks = [disk['Name'] for disk in self.call('list.vm.storage', host)]

		(disk_name, ) = self.fillParams([
			('disk', None, True)
		])

		if disk_name not in host_disks:
			raise ParamError(self, 'disk', f'{disk_name} not a defined disk on {host[0]}')
		vm_id = self.vm_id_by_name(host)

		self.db.execute(
			"""
			UPDATE virtual_machine_disks SET disk_delete = 1
			WHERE virtual_machine_disks.virtual_machine_id = %s
			AND virtual_machine_disks.disk_name = %s
			""",
			(vm_id, disk_name)
		)
