# @copyright@
import stack.commands


class Command(stack.commands.add.command):
	"""
	Add storage partition configuration for a host.

	<arg type='string' name='host' optional='1'>
	Hostname of the machine
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be added to
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be added to
	the database.
	</param>

	<example cmd='add host storage partition backend-0-1'>
	Adds the partition information for backend-0-1
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('add.storage.partition', self._argv + ['scope=host']))
		return self.rc
