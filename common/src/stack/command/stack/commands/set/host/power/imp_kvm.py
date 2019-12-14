# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.kvm
from stack.argument_processors.vm import VmArgumentProcessor
from stack.kvm import VmException
from collections import namedtuple

class Implementation(stack.commands.Implementation, VmArgumentProcessor):
	"""
	Implementation class for set host power.
	Communicates with kvm based hypervisors
	to manage virtual machine power states
	"""

	def run(self, args):
		host = args[0]
		output = []
		cmd = args[1]
		impl_output = args[2]
		kvmhost = self.get_hypervisor_by_name(host)

		# If either hypervisor attributes are not set
		# raise an error
		if not kvmhost:
			return impl_output('', f'No KVM host specified for virtual machine "{host}"', False)
		kvm = None

		try:
			kvm = stack.kvm.Hypervisor(kvmhost)
			if cmd == 'on':
				kvm.start_domain(host)
				output = impl_output('', '', True)
			elif cmd == 'off':
				kvm.stop_domain(host)
				output = impl_output('', '', True)

			# There isn't an actual reset
			# libvirt api call so just
			# stop and start the host
			elif cmd == 'reset':
				kvm.stop_domain(host)
				kvm.start_domain(host)
				output = impl_output('', '', True)
			elif cmd == 'status':

				# For a virtual machine there can be four statuses:
				# 1. On
				# 2. Off
				# 3. Undefined
				# 4. Connection failed to hypervisor
				#
				# For the power status we only want to show the first two
				# as the last two statuses can be treated as errors
				# in this context
				vm_status = self.owner.call('list.vm', args = [host, 'expanded=y'])[0].get('status')
				if vm_status and (vm_status != 'undefined' and ('Connection failed' not in vm_status)):
					output = impl_output(f'Chassis Power is {vm_status}', '', True)
				else:
					kvm.close()
					return impl_output('', f'Cannot find host {host} defined on hypervisor {kvmhost}', False)
		except VmException as msg:
			if kvm:
				kvm.close()
			return impl_output('', str(msg), False)
		kvm.close()
		return output
