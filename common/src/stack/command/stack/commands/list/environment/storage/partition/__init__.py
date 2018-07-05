# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List storage partition configuration for an environment.

	<arg type='string' name='host' optional='1'>
	Name of the environment
	</arg>

	<example cmd='list environment storage partition master_node'>
	lists the partition information for environment master_node
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=environment']))
		return self.rc
