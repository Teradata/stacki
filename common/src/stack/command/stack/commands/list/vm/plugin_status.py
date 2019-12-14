# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.kvm
from stack.kvm import VmException
from stack.argument_processors.vm import VmArgumentProcessor
from collections import defaultdict

class Plugin(stack.commands.Plugin, VmArgumentProcessor):

	def provides(self):
		return 'status'

	def requires(self):
		return ['basic']

	def run(self, args):
		hosts, expanded = args
		hypervisors = defaultdict()
		vm_status = defaultdict(list)
		keys = ['status']

		# Skip this plugin if no_status is set
		if not expanded:
			return {'keys': [], 'values': {} }

		for host in hosts:
			conn = None
			# Get the hypervisor hostname
			host_hypervisor = self.get_hypervisor_by_name(host)

			# If we already got the hypervisor status
			# from another host use that information
			# instead of reaching out to the hypervisor
			if hypervisors.get(host_hypervisor):
				guests = hypervisors[host_hypervisor]
				if guests.get(host):
					vm_status[host].append(guests[host])
				else:
					vm_status[host].append('undefined')
			else:
				try:
					conn = stack.kvm.Hypervisor(host_hypervisor)

					# A dict of the current status
					# of all VM's on the hypervisor
					guest_status = conn.guests()
					hypervisors[host_hypervisor] = guest_status
					if host in guest_status:
						vm_status[host].append(guest_status[host])
					else:
						vm_status[host].append('undefined')
					conn.close()

				# If an exception was raised, set the status
				# to connection failed
				except VmException as error:
					if conn:
						conn.close()
					vm_status[host].append('Connection failed to hypervisor')
		return { 'keys' : keys, 'values': vm_status }
