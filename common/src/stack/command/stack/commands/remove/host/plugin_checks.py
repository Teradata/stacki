# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError, ParamError
from stack.argument_processors.vm import VmArgumentProcessor

class Plugin(stack.commands.Plugin, VmArgumentProcessor):
	"""
	Prevent the removal of a virtual machine
	hypervisor host with virtual machines
	assigned to it
	"""

	def provides(self):
		return 'checks'

	def precedes(self):
		#
		# make sure this plugin runs first
		#
		return ['HEAD']

	def run(self, hosts):

		# Check that for a hypervisor appliance host
		# there are not any assigned VM's to it
		# at removal time
		for host in hosts:
			try:
				vm_hosts = self.owner.call('list.vm', [f'hypervisor={host}'])
				if vm_hosts:
					raise CommandError(self.owner, f'Cannot remove host {host} with virtual machines assigned')

			# If the given host isn't a valid hypervisor, list vm
			# will raise a param error
			except ParamError:
				continue
