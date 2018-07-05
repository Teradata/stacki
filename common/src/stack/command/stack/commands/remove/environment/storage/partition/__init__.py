# @copyright@
import stack.commands


class Command(stack.commands.remove.command):
	"""
	Remove storage partition information for an environment.

	<arg type='string' name='environment' optional='1'>
	Appliance name
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove environment storage partition master_node device=sda'>
	Removes the device sda partition information for the environment 'master_node'
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('remove.storage.partition', self._argv + [ 'scope=environment' ]))
		return self.rc
