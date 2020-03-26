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
	Set membership state on an infiniband partition in the Stacki database for
	a switch.

	<arg type='string' name='switch'>
	The name of the switches to add partition members to.
	</arg>

	<param type='string' name='name' optional='0'>
	The name of the partition to set membership status on the switch.
	</param>

	<param type='string' name='guid' optional='1'>
	The GUID of the host's infiniband interface to use.
	</param>

	<param type='string' name='member' optional='1'>
	The hostname with an infiniband interface to add as a member.  Must be
	specified with the name of the interface to use.
	</param>

	<param type='string' name='interface' optional='1'>
	The name of an infiniband interface to add as a member.  Must be specified
	with the name of the host the interface belongs to.
	</param>

	<param type='string' name='membership' optional='1'>
	The membership state to use for this member on the partition.  Must be 'both',
	or 'limited'.  Defaults to 'limited'.
	</param>

	<param type='boolean' name='enforce_sm' optional='1'>
	If a switch is not an infiniband subnet manager an error will be raised.
	</param>
	"""

	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'switch')

		name, guid, hostname, interface, membership, enforce_sm = self.fillParams([
			('name', None, True),
			('guid', None),
			('member', None),
			('interface', None),
			('membership', 'limited'),
			('enforce_sm', False),
		])

		if not guid and not hostname:
			raise CommandError(self, 'either guid or member and interface must be specified')

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

		name = name.lower()
		if name == 'default':
			name = 'Default'
		elif name != None:
			try:
				name = '0x{0:04x}'.format(int(name, 16))
			except ValueError:
				raise ParamValue(self, 'name', 'a hex value between 0x0001 and 0x7ffe, or "default"')

		membership = membership.lower()
		if membership not in ['limited', 'full']:
			raise ParamValue(self, 'membership', 'either "limited" or "full"')

		switches = self.getSwitchNames(args)
		switch_attrs = self.getHostAttrDict(switches)
		for switch in switches:
			if switch_attrs[switch].get('switch_type') != 'infiniband':
				raise CommandError(self, f'{switch} does not have a switch_type of "infiniband"')

		if self.str2bool(enforce_sm):
			enforce_subnet_manager(self, switches)

		switch, = switches
		switch_id = self.db.select('id FROM nodes WHERE name=%s', switch)[0][0]

		# ensure the guid actually exists - guid should be unique across table
		guid_id = self.db.select('id FROM networks WHERE mac=%s', guid)
		try:
			guid_id = guid_id[0][0]
		except IndexError:
			raise CommandError(self, f'guid "{guid}" was not found in the interfaces table')

		# lookups using sql instead of api calls because all 'list switch partition' calls are expensive.
		# Ensure this partition exists on the switch
		if self.db.count(
				'(id) FROM ib_partitions WHERE part_name=%s AND switch=%s',
				(name, switch_id)) == 0:
			raise CommandError(self, f'partition {name} does not exist on switch {switch}')

		# Determine if this member already exists on the partition and switch
		existing = False
		if self.db.count('''
			(ib_m.id)
			FROM ib_memberships ib_m, ib_partitions ib_p, nodes, networks
			WHERE ib_m.switch=nodes.id AND
				nodes.name=%s AND
				networks.id=ib_m.interface AND
				ib_m.part_name=ib_p.id AND
				ib_p.part_name=%s AND
				networks.id=%s ''',
				(switch, name, guid_id)) > 0:
			existing = True

		insert_sql = '''
				INSERT INTO ib_memberships (switch, interface, part_name, member_type)
				VALUES (%s,
						%s,
						(SELECT id FROM ib_partitions WHERE part_name=%s AND switch=%s),
						%s)
				'''

		update_sql = '''
				UPDATE ib_memberships
				SET switch=%s,
					interface=%s,
					part_name=(SELECT id FROM ib_partitions WHERE part_name=%s AND switch=%s),
					member_type=%s
				WHERE switch=%s AND
					part_name=(SELECT id FROM ib_partitions WHERE part_name=%s AND switch=%s) AND
					interface=%s
				'''

		if existing:
			self.db.execute(update_sql, (switch_id, guid_id, name, switch_id, membership, switch_id, name, switch_id, guid_id))
		else:
			self.db.execute(insert_sql, (switch_id, guid_id, name, switch_id, membership))
