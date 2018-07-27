# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List the storage controller configuration for an appliance.

	<example cmd='list appliance storage controller backend'>
	List appliance-specific storage controller configuration for
	appliance 'backend'.
	</example>

	<example cmd='list appliance storage controller'>
	List global storage controller configuration for all appliances.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.controller', self._argv + ['scope=appliance']))
		return self.rc
