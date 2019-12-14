# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import ParamError

class Command(stack.commands.list.vm.Command):
	"""
	List virtual machine storage information.

	<arg optional='1' type='string' name='host' repeat='1'>
	The name of a virtual machine host.
	</arg>

	<param type='string' name='hypervisor'>
	Only display hosts on a specific hypervisor.
	</param>

	<example cmd='list vm storage virtual-backend-0-0'>
	List virtual-backend-0-0 storage information.
	</example>

	<example cmd='list vm storage hypervisor=hypervisor-0-1'>
	List all disks belonging to virtual machines hosted on
	hypervisor-0-1
	</example>
	"""

	def run(self, param, args):
		hypervisor, = self.fillParams([
			('hypervisor', '')
		])

		# Get all valid virtual machine hosts
		hosts = self.valid_vm_args(args)
		hypervisor_hosts = []

		if hypervisor and not self.is_hypervisor(hypervisor):
			raise ParamError(self, 'hypervisor', f'{hypervisor} not a valid hypervisor')
		self.beginOutput()
		header = [
					'Virtual Machine',
					'Name',
					'Type',
					'Location',
					'Size',
					'Image Name',
					'Image Archive',
					'Mountpoint',
					'Pending Deletion'
		]

		# Remove any hosts not belonging to the hypervisor param
		# if it's set
		for vm in hosts:
			vm_hypervisor = self.get_hypervisor_by_name(vm)
			if hypervisor and vm_hypervisor != hypervisor:
				continue
			hypervisor_hosts.append(vm)

		vm_disks = self.get_all_disks(hypervisor_hosts)

		for vm_name, disks in vm_disks.items():
			if not disks:
				break
			for disk_id, disk_vals in disks.items():
				self.addOutput(owner = vm_name, vals = disk_vals)
		self.endOutput(header=header, trimOwner=False)
