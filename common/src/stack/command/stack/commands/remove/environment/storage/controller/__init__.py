# @copyright@
import stack.commands


class Command(stack.commands.remove.command):
	"""
	Remove a storage controller configuration for an environment.

	<param type='int' name='adapter' optional='1'>
	Adapter address. If adapter is '*', enclosure/slot address applies to
	all adapters.
	</param>

	<param type='int' name='enclosure' optional='1'>
	Enclosure address. If enclosure is '*', adapter/slot address applies
	to all enclosures.
	</param>

	<param type='int' name='slot'>
	Slot address(es). This can be a comma-separated list. If slot is '*',
	adapter/enclosure address applies to all slots.
	</param>

	<example cmd='remove environment storage controller master_node slot=1'>
	Remove the disk array configuration for slot 1 on the environment 'master_node'.
	</example>

	<example cmd='remove environment storage controller master_node slot=1,2,3,4'>
	Remove the disk array configuration for slots 1-4 for the environment 'master_node'.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('remove.storage.controller', self._argv + [ 'scope=environment' ]))
		return self.rc
