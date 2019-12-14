# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
import stack.commands


class Plugin(stack.commands.Plugin):
	"""
	Plugin to mark a specified virtual machine
	for deletion
	"""

	def provides(self):
		return 'host'

	def requires(self):
		return ['storage']

	def run(self, args):
		hosts, disks, nukedisks = args
		for host, host_id in hosts.items():
			self.owner.db.execute(
				"""
				UPDATE virtual_machines SET vm_delete = 1
				WHERE virtual_machines.id = %s
				""", (host_id, )
			)
