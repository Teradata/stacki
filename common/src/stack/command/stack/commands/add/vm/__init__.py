# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.argument_processors.vm import VmArgumentProcessor
from stack.exception import CommandError, ArgRequired, ParamError

class command(
	stack.commands.HostArgumentProcessor,
	stack.commands.add.command
):
	pass

class Command(command, VmArgumentProcessor):
	"""
	Add a new virtual machine host to the cluster.

	<arg type='string' name='hypervisor' optional='1'>
	The name of the hypervisor the virtual machine is to be hosted on.
	Must be a valid host with an appliance configured to host virtual machines
	(depending on the infrastructure it could be different appliances).
	</arg>

	<param type='string' name='cpu'>
	The number of cpu cores to give to the virtual host.
	</param>

	<param type='string' name='memory'>
	The amount of memory in MB to give to the virtual host.
	</param>

	<param type='string' name='storage_pool' optional='1'>
	The location on the hypervisor to store and create disk images.
	Must be the full path. Required if disks are not just mountpoints.
	</param>

	<param type='string' name='disks'>
	A list of disks or single disk for a virtual machine. Can be an integer to
	create a new disk image for the virtual machine, a full path to a qcow2 or raw image,
	or a path to a disk device on the hypervisor (such as /dev/sdb) to mount to a virtual machine.
	</param>

	"""

	def run(self, params, args):
		vm_host = self.getSingleHost(args)

		hypervisor, cpu, memory, disk_loc, disks = self.fillParams([
			('hypervisor', None, True),
			('cpu', '1'),
			('memory', '3072'),
			('storage_pool', ''),
			('disks', 100)
		])

		if not self.is_hypervisor(hypervisor):
			raise ParamError(self, param = 'hypervisor', msg = f'has a non valid hypervisor appliance or host')

		# CPU and Memory input must be valid numbers and be at least equal to one
		if not memory.isdigit() or int(memory) < 1:
			raise ParamError(self, 'memory', 'must be a number greater than 0')

		if not cpu.isdigit() or int(cpu) < 1:
			raise ParamError(self, 'cpu', 'must be a number greater than 0')

		# Check if the virtual machine is already defined
		# Raise a CommandError if it is
		if self.vm_by_name(vm_host):
			raise CommandError(self, f'Virtual Machine {vm_host} already defined')

		# Add into database
		self.db.execute("""
			insert into virtual_machines
			(hypervisor_id, node_id, memory_size, cpu_cores)
			values (
				(select nodes.id from nodes where name=%s),
				(select nodes.id from nodes where name=%s),
				%s, %s
			)
		""", (hypervisor, vm_host, int(memory), int(cpu)))

		# Call add vm storage for any disks given
		self.call('add.vm.storage', [vm_host, f'disks={disks}', f'storage_pool={disk_loc}'])
