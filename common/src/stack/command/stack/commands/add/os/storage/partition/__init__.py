# @copyright@
import stack.commands


class Command(stack.commands.add.command):
	"""
	Add storage partition configuration for an os type.

	<arg type='string' name='os' optional='1'>
	OS Name
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be added to
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be added to
	the database.
	</param>

	<example cmd='add os storage partition redhat'>
	Adds the partition information for redhat os type
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('add.storage.partition', self._argv + ['scope=os']))
		return self.rc
