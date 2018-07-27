# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'storage controller'

	def run(self, appliance):
		self.owner.command('remove.appliance.storage.controller', [appliance, 'slot=*'])