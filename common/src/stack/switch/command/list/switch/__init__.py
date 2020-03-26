# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.bool import str2bool
import stack.commands
from stack.commands import SwitchArgProcessor
import stack.util

class command(SwitchArgProcessor, stack.commands.list.command):
	pass

class Command(command):
	"""
	List Appliance, physical position, and model of any hosts with appliance type
	of `switch`.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplies, info about
	all the known switches is listed.
	</arg>

	<param type='boolean' name='expanded'>
	If set to True, list additional switch information provided by plugins which
	may require slower lookups.
	Default is False.
	</param>

	<example cmd='list host switch-0-0'>
	List info for switch-0-0.
	</example>

	<example cmd='list switch'>
	List info for all known switches/
	</example>
	"""
	def run(self, params, args):
		
		(order, expanded) = self.fillParams([
			('order', 'asc'),
			('expanded', False),
		])

		self.expanded = str2bool(expanded)

		switches = self.getSwitchNames(args)

		header = ['switch']
		values = {}
		for switch in switches:
			values[switch] = []

		for (provides, result) in self.runPlugins(switches):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h].extend(v)

		self.beginOutput()
		for switch in switches:
			if values[switch]:
				self.addOutput(switch, values[switch])
		self.endOutput(header=header, trimOwner=False)

