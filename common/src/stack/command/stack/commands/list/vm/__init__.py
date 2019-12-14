# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.argument_processors.vm import VmArgumentProcessor
from stack.exception import CommandError, ParamError

class command(stack.commands.HostArgumentProcessor,
        stack.commands.list.command):
        pass

class Command(command, VmArgumentProcessor):
	"""
	List virtual machines on defined on a hypervisor with their current status.

	<arg optional='1' type='string' name='host' repeat='1'>
	The virtual hosts to list.
	</arg>

	<param type='string' name='hypervisor'>
	Only display hosts on a specific hypervisor.
	</param>

	<example cmd='list vm'>
	List all virtual machines with their statuses (on, off, or not defined)
	</example>

	<example cmd='list vm virtual-backend-0-0'>
	Only list virtual-backend-0-0
	</example>

	<example cmd='list vm hypervisor=hypervisor-0-1'>
	Only list virtual machines assigned to hypervisor-0-1
	</example>
	"""

	def run(self, param, args):
		vm_hosts = self.valid_vm_args(args)
		hypervisor, expanded = self.fillParams([
			('hypervisor', ''),
			('expanded', False)
		])

		# Expanded shows the actual VM
		# status on the hypervisor
		expanded = self.str2bool(expanded)

		if hypervisor and not self.is_hypervisor(hypervisor):
			raise ParamError(self, param = 'hypervisor', msg = f'{hypervisor} is not a valid hypervisor')
		header = ['virtual machine']
		vm_values = {}

		# Check the host args have the correct hypervisor if that
		# param is set
		for vm_host in vm_hosts:
			host_hypervisor = self.get_hypervisor_by_name(vm_host)
			if hypervisor and hypervisor != host_hypervisor:
				continue
			vm_values[vm_host] = []
		self.beginOutput()

		# Run the various plugins for VM information and gather the results
		# for output
		for (provides, result) in self.runPlugins((vm_values.keys(), expanded)):
			header.extend(result['keys'])
			for vm_host, vm_value in result['values'].items():
				vm_values[vm_host].extend(vm_value)
		self.beginOutput()
		for host, values in vm_values.items():
			self.addOutput(host, values)
		self.endOutput(header=header, trimOwner=False)
