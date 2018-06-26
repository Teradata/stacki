# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.exception import CommandError

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.list.command,
	      stack.commands.HostArgumentProcessor):
	pass

class Command(command):
	"""
	List mac address table on switch.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplies, info about
	all the known switches is listed.
	</arg>

	<param optional='1' type='bool' name='pinghosts'>
	Send a ping to each host connected to the switch. Hosts do not show up in the
	mac address table if there is no traffic.
	</param>

	<example cmd='list host mac switch-0-0'>
	List mac table for switch-0-0.
	</example>

	<example cmd='list switch mac'>
	List mac table for all known switches/
	</example>
	"""
	def run(self, params, args):

		(pinghosts,) = self.fillParams([
		('pinghosts', False),
		])

		self.pinghosts = self.str2bool(pinghosts)

		_switches = self.getSwitchNames(args)
		self.beginOutput()
		for switch in self.call('list.host.interface', _switches):

			switch_name = switch['host']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [switch])

		self.endOutput(header=['switch', 'port',  'mac', 'host', 'interface', 'vlan'])
