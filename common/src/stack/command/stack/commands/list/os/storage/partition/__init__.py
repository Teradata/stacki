# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List storage partition configuration for an os type.

	<arg type='string' name='os' optional='1'>
	OS Name
	</arg>

	<example cmd='add os storage partition redhat'>
	Lists the partition information for redhat os type
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=os']))
		return self.rc
