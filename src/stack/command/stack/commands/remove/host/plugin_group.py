# @SI_Copyright@
# @SI_Copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'group'

	def run(self, host):
		self.owner.db.execute("""
			delete
			from memberships
			where nodeid = (select id from nodes where name = '%s') """ %
			(host))
