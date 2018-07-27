# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List the storage controller configuration for an os.

	<example cmd='list os storage controller redhat'>
	List os-specific storage controller configuration for
	os 'redhat'.
	</example>

	<example cmd='list os storage controller'>
	List global storage controller configuration for all oses.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.controller', self._argv + [ 'scope=os' ]))
		return self.rc
