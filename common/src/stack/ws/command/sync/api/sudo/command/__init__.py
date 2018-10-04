# @copyright@
# @copyright@

import os
import stack.commands
import stack.commands.sync

class Command(stack.commands.sync.command):
	"""
	Sync the sudoers.d file on the frontend

	<dummy />
	"""
	def run(self, params, args):
		self.report("report.api.sudo.command")
