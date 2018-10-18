# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import shlex
from operator import itemgetter
from collections import namedtuple

IfInfo = namedtuple('IfInfo', ['host', 'interface', 'network', 'mac', 'ip', 'options'])
iface_getter = itemgetter('host', 'interface', 'network', 'mac', 'ip', 'options')

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchException
from stack.switch.m7800 import SwitchMellanoxM7800


class Implementation(stack.commands.Implementation):


	def nuke(self, switch_handle):
		for part in switch_handle.partitions:
			switch_handle.del_partition(part)

		switch_handle.wipe_ssh_keys()


	def get_fabric(self, switch):
		fabric = ''
		for row in self.owner.call('list.host.interface', [switch]):
			iface = IfInfo(*iface_getter(row))
			if iface.host != switch:
				continue

			if not iface.interface.startswith('mgmt'):
				continue
			if not iface.mac or not iface.ip:
				# mgmt iface not configured
				continue

			if iface.options is None:
				# no partition info set
				continue

			opts = shlex.split(iface.options)

			if 'ibfabric=' not in iface.options:
				# no fabric info set
				continue
			_, fabric = next(opt.split('=') for opt in opts if opt.startswith('ibfabric='))
			break

		return fabric


	def get_db_partitions(self, switch):
		partitions = {}
		list_part_member = self.owner.call('list.switch.partition.member', [switch, 'expanded=true'])
		for row in list_part_member:
			part = row['partition']
			if part not in partitions:
				partitions[part] = {
					'guids': {},
					'pkey': row['partition key']
				}

				opts = dict(flag.split('=') for flag in row['options'].split() if '=' in flag)
				if 'ipoib' in opts and opts['ipoib'] == 'True':
					partitions[part]['ipoib'] = True
				elif 'ipoib' in opts and opts['ipoib'] == 'False':
					partitions[part]['ipoib'] = False

				if 'defmember' in opts:
					partitions[part]['defmember'] = opts['defmember']

			guid = row['guid'][-23:].lower()
			partitions[part]['guids'][guid] = row['membership']

		return partitions


	def run(self, args):
		switch, = args

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('switch_username'),
			'password': switch_attrs[switch].get('switch_password'),
		}

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(switch, **kwargs)
		s.connect()
		if self.owner.nukeswitch:
			self.nuke(s)
			return

		try:
			pubkey = open('/root/.ssh/id_rsa.pub').read()
			s.ssh_copy_id(pubkey.strip())
		except FileNotFoundError:
			pass

		if not s.subnet_manager:
			raise CommandError(self.owner, f'{switch} is not a subnet manager')

		fabric = self.get_fabric(switch)
		db_partitions = self.get_db_partitions(switch)

		# remove partitions on the switch which are not on the database
		# handling changes within existing partitions will be handled later
		unused_partitions = set(s.partitions).difference(db_partitions)
		for part in unused_partitions:
			s.del_partition(part)

		if not fabric:
			raise CommandError(self.owner, 'no fabric specified')

		# for each partition in the database, add if it doesn't exist, 
		live_partitions = s.partitions
		for part in db_partitions:
			if part not in live_partitions:
				# create the partitions that don't exist yet
				kwargs = {k:v for k,v in db_partitions[part].items() if k in ['ipoib', 'defmember']}
				s.add_partition(part,
								int(db_partitions[part]['pkey'], 16),
								**kwargs
								)

				# leave an empty dictionary so that later set()-builders don't break
				live_partitions[part] = {'guids': {}}

			# get all of the members on the switch for this partition who aren't in the DB
			db_part_members   = set(db_partitions[part]['guids'])
			live_part_members = set(live_partitions[part]['guids'])
			old_members       = live_part_members.difference(db_part_members)

			# remove the old partition members
			[s.del_partition_member(part, member) for member in old_members]

			# create the new memberships.
			# note: it's safe to overwrite the old ones this way as well
			for guid in db_part_members:
				membership = db_partitions[part]['guids'][guid]
				s.add_partition_member(part, guid, membership)
