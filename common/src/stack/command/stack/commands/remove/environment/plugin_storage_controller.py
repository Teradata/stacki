# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'storage controller'

	def run(self, env):
		self.owner.command('remove.environment.storage.controller', [env, 'slot=*'])