# @copyright@
import stack.commands


class Command(stack.commands.remove.command):
	"""
	Remove storage partition information for an appliance.

	<arg type='string' name='appliance' optional='1'>
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

	<example cmd='remove appliance storage partition backend'>
	Removes the partition information for backend appliances
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('remove.storage.partition', self._argv + [ 'scope=appliance' ]))
		return self.rc
