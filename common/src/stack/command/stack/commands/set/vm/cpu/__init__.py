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
	Set the number of cpu cores allocated to a virtual machine.

	<arg type='string' name='host' repeat='1'>
	One or more virtual machine host names.
	</arg>

	<param type='string' name='cpu' optional='0'>
	The number of cpu cores to allocate to the host.
	Must be a value of at least be one or more.
	</param>

	<example cmd='set vm cpu virtual-backend-0-2 cpu=4'>
	Set the cpu core's allocated to virtual-backend-0-2
	to 4 cores.
	</example>
	"""

	def run(self, params, args):
		hosts = self.valid_vm_args(args)

		cpu_cores, = self.fillParams([
			('cpu', None, True)
		])

		if not cpu_cores.isdigit() or int(cpu_cores) < 1:
			raise ParamError(self, 'cpu', 'must be a valid integer and greater than or equal to 1.')

		for vm in hosts:
			vm_id = self.vm_id_by_name(vm)
			self.db.execute(
				"""
				UPDATE virtual_machines SET cpu_cores=%s
				WHERE virtual_machines.id=%s
				""",
				(cpu_cores, vm_id)
			)
