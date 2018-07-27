# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'storage controller'

	def run(self, hosts):
		for host in hosts:
			self.owner.command('remove.host.storage.controller', [host, 'slot=*'])