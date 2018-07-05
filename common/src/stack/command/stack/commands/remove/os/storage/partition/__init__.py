# @copyright@
import stack.commands


class Command(stack.commands.remove.command):
	"""
	Remove storage partition configuration for an os type.

	<arg type='string' name='os' optional='1'>
	OS Name
	</arg>

	<param type='string' name='device' optional='1'>
	Device whose partition configuration needs to be removed from
	the database.
	</param>

	<param type='string' name='mountpoint' optional='1'>
	Mountpoint for the partition that needs to be removed from
	the database.
	</param>

	<example cmd='remove os storage partition redhat device=sda'>
	Removes the device sda partition information for the os 'redhat'
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('remove.storage.partition', self._argv + [ 'scope=os' ]))
		return self.rc
