# @copyright@
import stack.commands


class Command(stack.commands.list.command):
	"""
	List storage partition configuration for an appliance.

	<arg type='string' name='appliance' optional='1'>
	Appliance name
	</arg>

	<example cmd='list appliance storage partition backend>
	lists the partition information for for backend appliances
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=appliance']))
		return self.rc
