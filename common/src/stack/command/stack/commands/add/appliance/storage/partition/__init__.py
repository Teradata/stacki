# @copyright@
import stack.commands


class Command(stack.commands.add.command):
	"""
	Add storage partition configuration for an appliance.

	<arg type='string' name='appliance' optional='1'>
	Appliance name
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be added to
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be added to
	the database.
	</param>

	<example cmd='add appliance storage partition backend'>
	Adds the partition information for backend appliances
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('add.storage.partition', self._argv + ['scope=appliance']))
		return self.rc
