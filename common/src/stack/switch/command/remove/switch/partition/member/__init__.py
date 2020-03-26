# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import SwitchArgProcessor
from stack.commands.sync.switch.ib import enforce_subnet_manager
from stack.exception import ArgUnique, ParamValue, CommandError


class Command(SwitchArgProcessor, stack.commands.Command):
	"""
	Remove memberships from infiniband partitions from the Stacki database.

	<arg type='string' name='switch'>
	The name of the switches to remove membership on.
	</arg>

	<param type='string' name='name' optional='1'>
	The name of the partition the member is a part of.
	</param>

	<param type='string' name='guid' optional='1'>
	The GUID of the host's infiniband interface to use.
	</param>

	<param type='string' name='member' optional='1'>
	The hostname with an infiniband interface to remove membership for.  Must be
	specified with the name of the interface to use.
	</param>

	<param type='string' name='interface' optional='1'>
	The name of an infiniband interface to remove membership for.  Must be specified
	with the name of the host the interface belongs to.
	</param>

	<param type='boolean' name='enforce_sm' optional='1'>
	If a switch is not an infiniband subnet manager an error will be raised.
	</param>

	"""

	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'switch')

		name, guid, hostname, interface, enforce_sm = self.fillParams([
			('name', None),
			('guid', None),
			('member', None),
			('interface', None),
			('enforce_sm', False),
		])

		if guid:
			guid = guid.lower()
		if hostname and not interface or interface and not hostname:
			raise CommandError(self, 'member and interface must both be specified')
		elif hostname and interface:
			ifaces = self.call('list.host.interface', [hostname])
			for row in ifaces:
				if row['interface'] == interface:
					guid = row['mac']
					break
			else: #nobreak
				raise CommandError(self, f'member has no interface named "{interface}"')

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

		switch, = switches
		switch_id, = self.db.select('id FROM nodes WHERE name=%s', switch)

		vals = [switch_id[0]]
		delete_stmt = '''DELETE FROM ib_memberships'''
		where_clause = 'WHERE ib_memberships.switch=%s'
		if name:
			part_id = self.db.select('id FROM ib_partitions WHERE part_name=%s AND switch=%s', (name, switch_id))
			if not part_id:
				raise CommandError(self, f'{name} is not a partition on {switches[0]}')
			where_clause += ' AND ib_memberships.part_name=%s'
			vals.append(part_id[0][0])

		if guid:
			where_clause += ' AND ib_memberships.interface=(SELECT id FROM networks WHERE mac=%s)'
			vals.append(guid)

		self.db.execute(f'{delete_stmt} {where_clause}', vals)
