# @SI_Copyright@
# @SI_Copyright@

import subprocess
import stack.commands

class Command(stack.commands.sync.host.command):

	def run(self, params, args):

		self.notify('Sync Host Boot\n')

		argv = self.getHostnames(args, managed_only=True)
		argv.append('notify=true')
		self.report('report.host.bootfile', argv)
