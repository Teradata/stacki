# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
import stack.commands
from stack import api

class Plugin(stack.commands.Plugin):
	"""
	Plugin for marking a virtual machine
	disk for deletion
	"""
	def provides(self):
		return 'storage'

	def run(self, args):
		hosts, disks, nukedisks = args
		if all([nukedisks, hosts, disks]):
			for host, host_id in hosts.items():
				for disk in disks:
					if disk['Virtual Machine'] == host:
						api.Call('remove.vm.storage', args = [host, f'disk={disk["Name"]}'])
