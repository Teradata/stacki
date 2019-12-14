# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import ParamError

class Command(stack.commands.set.vm.command):
	"""
	Set the hypervisor hostname to host a virtual machine.

	<arg type='string' name='host' repeat='1'>
	One or more hostnames.
	</arg>

	<param type='string' name='hypervisor' optional='0'>
	The hostname of the hypervisor to host a virtual machine.
	</param>

	<example cmd='set vm hypervisor virtual-backend-0-2 hypervisor=hypervisor-host-0-1'>
	Assign hypervisor-host-0-1 to host virtual-backend-0-2.
	</example>
	"""

	def run(self, params, args):
		hosts = self.valid_vm_args(args)

		(hypervisor, ) = self.fillParams([
			('hypervisor', '', True)
		])

		if not self.is_hypervisor(hypervisor):
			raise ParamError(self, 'hypervisor', f'host {hypervisor} is not a valid hypervisor')

		for vm in hosts:
			vm_id = self.vm_id_by_name(vm)
			hypervisor_id = self.hypervisor_id_by_name(hypervisor)
			self.db.execute(
				"""
				UPDATE virtual_machines SET hypervisor_id=%s
				WHERE virtual_machines.id=%s
				""",
				(hypervisor_id, vm_id)
			)
