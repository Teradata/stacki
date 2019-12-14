# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError

class Plugin(stack.commands.Plugin):
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
			host_appliance = self.owner.getHostAttr(host, 'appliance')
			if host_appliance != 'hypervisor':
				return
			vm_hosts = self.owner.call('list.vm', [f'hypervisor={host}'])
			if vm_hosts:
				raise CommandError(self.owner, f'Cannot remove host {host} with virtual machines assigned')
