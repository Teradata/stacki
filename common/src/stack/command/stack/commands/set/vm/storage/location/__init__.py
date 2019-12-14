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
	Set the VM disk location on the hypervisor.

	<arg type='string' name='host' repeat='1'>
	The virtual machine host the disk is assigned to.
	</arg>

	<param type='string' name='disk' optional='1'>
	The disk to set a new hypervisor location to.
	</param>

	<param type='string' name='location' optional='1'>
	The new location the disk will be placed
	</param>

	<example cmd='set vm storage location virtual-backend-0-1 disk=sda location=/export/pools/stacki'>
	Have the storage backing of disk sda be placed at /export/pools/stacki
	</example>
	"""

	def run(self, params, args):
		hosts = self.getSingleHost(args)
		hosts = self.valid_vm_args(args)
		disk_name, location = self.fillParams([
			('disk', '', True),
			('location', '', True)
		])

		for vm in hosts:
			disks = self.call('list.vm.storage', hosts)
			host_disks = [disk['Name'] for disk in disks]
			if disk_name not in host_disks:
				raise ParamError(self, 'disk', f'{disk_name} is not a valid disk for {vm}')
			vm_id = self.vm_id_by_name(vm)

			self.db.execute(
				"""
				UPDATE virtual_machine_disks SET disk_location=%s
				WHERE virtual_machine_disks.disk_name = %s
				AND virtual_machine_disks.virtual_machine_id = %s
				""",
				(location, disk_name, vm_id)
			)
