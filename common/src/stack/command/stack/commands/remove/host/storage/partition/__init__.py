# @copyright@
import stack.commands


class Command(stack.commands.remove.command):
	"""
	Remove storage partition configuration for a host.

	<arg type='string' name='host' optional='1'>
	Hostname of the machine
	</arg>
	
	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove host storage partition backend-0-1'>
	Removes the partition information for backend-0-1
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('remove.storage.partition', self._argv + [ 'scope=host' ]))
		return self.rc
