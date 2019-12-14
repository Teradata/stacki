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
	Allocate memory to a virtual machine host.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='memory' optional='0'>
	The amount of memory in MB to allocate to a virtual machine host.
	</param>

	<example cmd='set vm memory virtual-backend-0-2 memory=4096'>
	Allocate 4096MB of memory to virtual-backend-0-2
	</example>
	"""

	def run(self, params, args):
		hosts = self.valid_vm_args(args)

		memory, = self.fillParams([
			('memory', 3072, True)
		])

		if not memory.isdigit() or int(memory) < 1:
			raise ParamError(self, 'memory', 'must be a valid integer and greater than or equal to one')

		for vm in hosts:
			vm_id = self.vm_id_by_name(vm)
			self.db.execute(
				"""
				UPDATE virtual_machines SET memory_size=%s
				WHERE virtual_machines.id=%s
				""",
				(memory, vm_id)
			)
