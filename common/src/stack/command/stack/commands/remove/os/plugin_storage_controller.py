# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'storage controller'

	def run(self, os):
		self.owner.command('remove.os.storage.controller', [os, 'slot=*'])