# @copyright@
import stack.commands


class Command(stack.commands.remove.command):
	"""
	Remove a storage controller configuration for a host.

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

	<example cmd='remove host storage controller backend-0-0 slot=1'>
	Remove the disk array configuration for slot 1 on the host 'backend-0-0'.
	</example>

	<example cmd='remove host storage controller backend-0-0 slot=1,2,3,4'>
	Remove the disk array configuration for slots 1-4 for the host 'backend-0-0'.
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('remove.storage.controller', self._argv + ['scope=host']))
		return self.rc
