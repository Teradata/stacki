# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import SwitchArgProcessor
from stack.commands.sync.switch.ib import enforce_subnet_manager
from stack.exception import ArgRequired, ParamValue, CommandError


class Command(SwitchArgProcessor, stack.commands.Command):
	"""
	Lists the infiniband partitions in the Stacki database for one or more
	switches.

	<arg type='string' name='switch'>
	The name of the switches to list partitions for.
	</arg>

	<param type='string' name='name' optional='1'>
	The name of the partition to list on the switch(es).
	</param>

	<param type='boolean' name='enforce_sm' optional='1'>
	If a switch is not an infiniband subnet manager an error will be raised.
	</param>

	"""

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'switch')

		name, enforce_sm = self.fillParams([
			('name', None),
			('enforce_sm', False),
		])

		if name:
			name = name.lower()
		if name == 'default':
			name = 'Default'
		elif name != None:
			try:
				name = '0x{0:04x}'.format(int(name, 16))
			except ValueError:
				raise ParamValue(self, 'name', 'a hex value between 0x0001 and 0x7ffe, or "default"')

		switches = self.getSwitchNames(args)
		switch_attrs = self.getHostAttrDict(switches)
		for switch in switches:
			if switch_attrs[switch].get('switch_type') != 'infiniband':
				raise CommandError(self, f'{switch} does not have a switch_type of "infiniband"')

		if self.str2bool(enforce_sm):
			enforce_subnet_manager(self, switches)

		format_str = ','.join(['%s'] * len(switches))
		sw_select = '''
			nodes.name, ib.part_name, ib.part_key, ib.options
			FROM nodes, ib_partitions ib
			WHERE nodes.name IN (%s)
			AND nodes.id=ib.switch''' % format_str

		vals = list(switches)

		if name:
			sw_select += ' AND ib.part_name=%s'
			vals.append(name)

		sw_select += ' ORDER BY nodes.name'

		self.beginOutput()
		for line in self.db.select(sw_select, vals):
			self.addOutput(line[0], (line[1], '0x{0:04x}'.format(line[2]), line[3]))
		self.endOutput(header=['switch', 'partition', 'partition key', 'options'])
