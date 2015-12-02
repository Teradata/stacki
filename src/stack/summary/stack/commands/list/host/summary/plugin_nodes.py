import stack.commands

class Plugin(stack.commands.Plugin):
	def provides(self):
		return "nodes"

	def requires(self):
		return []

	def run(self, params):
		self.owner.addOutput('localhost',
			('Host Count',
			len(self.owner.hosts)))
