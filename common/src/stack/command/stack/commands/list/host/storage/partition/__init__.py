# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List storage partition configuration for a host.

	<arg type='string' name='host' optional='1'>
	Hostname of the machine
	</arg>

	<example cmd='list host storage partition backend-0-1'>
	lists the partition information for backend-0-1
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=host']))
		return self.rc
