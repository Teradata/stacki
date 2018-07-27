# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List the storage controller configuration for an environment.

	<example cmd='list environment storage controller master_node'>
	List environment-specific storage controller configuration for
	environment 'master_node'.
	</example>

	<example cmd='list environment storage controller'>
	List global storage controller configuration for all environments.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.controller', self._argv + ['scope=environment']))
		return self.rc
