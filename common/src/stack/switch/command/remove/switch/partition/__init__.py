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
	Remove infiniband partitions from the Stacki database for one or more
	switches.

	<arg type='string' name='switch'>
	The name of the switches to remove partitions for.
	</arg>

	<param type='string' name='name' optional='1'>
	The name of the partition to remove from the switch(es).
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

		ids_sql = 'name, id FROM nodes WHERE name IN (%s)' % ','.join(['%s'] * len(switches))
		sw_ids = dict((row[0], row[1]) for row in self.db.select(ids_sql, tuple(switches)))

		format_str = ','.join(['%s'] * len(switches))
		delete_stmt = '''
			DELETE from ib_partitions
			WHERE switch IN (%s)''' % format_str
							   
		vals = list(sw_ids.values())

		if name:
			delete_stmt += ' AND ib_partitions.part_name=%s'
			vals.append(name)

		self.db.execute(delete_stmt, vals)
