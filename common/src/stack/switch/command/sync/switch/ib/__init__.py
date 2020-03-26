# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import subprocess

import stack.commands
from stack.commands import SwitchArgProcessor
from stack.exception import CommandError
import stack.util

def enforce_subnet_manager(command_handle, switches):
	ibswitches = [sw for sw in command_handle.call('list.switch', switches + ['expanded=True'])
			if sw['model'] == 'm7800' and sw['ib subnet manager']]

	bad_switches = set(switches).difference(sw['switch'] for sw in ibswitches)
	if bad_switches:
		msg = 'The following switches are either non-infiniband or are not subnet managers: '
		raise CommandError(command_handle, msg + f'{", ".join(bad_switches)}')

class command(SwitchArgProcessor, stack.commands.sync.command):
		pass

class Command(command):
	"""
	Reconfigure Infiniband switches.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more ib switch names. If no switch names are supplied,
	all switches will be reconfigured.  All switches will have root's
	public key uploaded, and if `nukeswitch` is True, all will be wiped.
	Only switches which are currently subnet managers will have any other
	configuration applied.
	</arg>

	<param type='boolean' name='nukeswitch' optional='1'>
	If 'yes', then put the switch into a default state (e.g., no vlans, no partitions),
	Just a "flat" switch.
	Default: no
	</param>

	<example cmd="sync switch infiniband-0-0">
	Reconfigure and set startup configuration on infiniband-0-0.
	</example>

	<example cmd="sync switch">
	Reconfigure all switches.
	</example>
	"""

	def run(self, params, args):

		nukeswitch, factory_reset, = self.fillParams([
			('nukeswitch', False),
			('factory_reset', False),
		])

		self.nukeswitch = self.str2bool(nukeswitch)
		self.factory_reset = self.str2bool(factory_reset)

		switches = self.getSwitchNames(args)

		switch_attrs = self.getHostAttrDict(switches)

		for switch in switches:
			if switch_attrs[switch].get('switch_type') != 'infiniband':
				msg = f'{switch} is not an infiniband switch, please verify "stack list host attr {switch} attr=switch_type"'
				raise CommandError(self, msg)

		for switch in self.call('list.host.interface', switches):
			switch_name = switch['host']

			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(switch_attrs[switch_name]['component.model'], [switch_name])

