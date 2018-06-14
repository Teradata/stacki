# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import shlex
from operator import itemgetter
from collections import namedtuple
from itertools import groupby

IfInfo = namedtuple('IfInfo', ['host', 'interface', 'network', 'mac', 'ip', 'options'])

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchException
from stack.switch.m7800 import SwitchMellanoxM7800


class Implementation(stack.commands.Implementation):


	def nuke(self, switch_handle):
		for part in switch_handle.partitions:
			switch_handle.del_partition(part)

		# other stuff goes here, but that's the big deal

	def run(self, args):
		switch = args[0]['host']

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('username'),
			'password': switch_attrs[switch].get('password'),
		}

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(switch, **kwargs)
		s.connect()
		if self.owner.nukeswitch:
			self.nuke(s)
			return

		if not s.subnet_manager:
			return

		# ensure default partition exists
		s.add_partition('Default')

		lst_host_appliances = dict(
			(k, next(v)) for k, v in groupby(self.owner.call('list.host'), itemgetter('host'))
		)
		lst_host_iface = self.owner.call('list.host.interface')

		iface_getter = itemgetter('host', 'interface', 'network', 'mac', 'ip', 'options')

		fabric = ''

		# good_partitions is the list of partitions we're either going to create or keep using
		good_partitions = []
		# first create the partitions
		for row in lst_host_iface:
			iface = IfInfo(*iface_getter(row))
			if iface.host != switch:
				continue

			if not iface.interface.startswith('mgmt'):
				continue
			if not iface.mac or not iface.ip:
				# mgmt inface not configured
				continue

			if iface.options is None:
				# no partition info set
				continue

			opts = shlex.split(iface.options)

			if 'ibfabric=' not in iface.options:
				# no fabric info set
				continue
			_, fabric = next(opt.split('=') for opt in opts if opt.startswith('ibfabric='))

			if 'ibpartition=' not in iface.options:
				# no partition info set
				continue
			_, partitions = next(opt.split('=') for opt in opts if opt.startswith('ibpartition='))

			# create partitions
			for part in partitions.split(','):
				try:
					# error or ignore?
					partition = '0x%04d' % int(part)
				except (ValueError, IndexError):
					continue

				if partition in s.partitions:
					good_partitions.append(partition)
					continue

				try:
					s.add_partition(partition, int(partition, 16))
					good_partitions.append(partition)
				except SwitchException as e:
					msg = f'Error while attempting to add partition "{partition}" to {switch}:\n{e}'
					raise CommandError(self.owner, msg)

		unused_partitions = set(s.partitions).difference(good_partitions)
		for part in unused_partitions:
			s.del_partition(part)

		if not fabric:
			raise CommandError(self.owner, 'no fabric specified')

		if 'Default' not in s.partitions:
			s.add_partition('Default')

		# by default, all compute hosts should be added to the Default partition as limited members
		# in the absence of an actual partitions hosts should be added as full members to Default
		macs_for_default = []
		# for backend nodes, we're looking for 'ibpartition' specified in the 'options' field of ibN ifaces
		for row in lst_host_iface:
			iface = IfInfo(*iface_getter(row))

			if lst_host_appliances[iface.host]['appliance'] == 'switch':
				# ib switches don't have their own interfaces listed
				# so this is probably the ethernet mgmt port
				continue

			if not iface.interface.startswith(fabric):
				# not an ib iface or not on the right fabric
				continue
			if not iface.mac:
				# no guid
				continue

			# all netapp arrays should be added as Full members to the default
			if lst_host_appliances[iface.host]['appliance'] == 'netapp_array':
				s.add_partition_member('Default', iface.mac[-23:], membership='full')
			else:
				macs_for_default.append(iface.mac)

			if iface.options is None:
				# no partition info set
				continue
			if 'ibpartition=' not in iface.options:
				# no partition info set
				continue

			opts = shlex.split(iface.options)
			_, partitions = next(opt.split('=') for opt in opts if opt.startswith('ibpartition='))

			# we know there's an '=', so this is safe
			for part in partitions.split(','):
				try:
					# error or ignore?
					partition = '0x%04d' % int(part)
				except (ValueError, IndexError):
					continue

				if partition not in s.partitions:
					# skip adding members for non-existant partitions
					continue

				s.add_partition_member(partition, iface.mac[-23:], membership='full')

		# if the only partition is 'Default', everyone should be a full member
		membership = 'limited'
		if list(s.partitions.keys()) == ['Default']:
			membership = 'full'

		for mac in macs_for_default:
			s.add_partition_member('Default', mac[-23:], membership=membership)
