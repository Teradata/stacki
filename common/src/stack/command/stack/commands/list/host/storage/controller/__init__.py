# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List the storage controller configuration for a host.

	<example cmd='list host storage controller backend-0-0'>
	List host-specific storage controller configuration for
	host 'backend-0-0'.
	</example>

	<example cmd='list host storage controller'>
	List global storage controller configuration for all hosts.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.controller', self._argv + [ 'scope=host' ]))
		return self.rc
