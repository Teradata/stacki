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


	def get_needed_partitions(self, switch, interface_data):
		fabric = ''
		# good_partitions is the list of partitions we're either going to create or keep using
		good_partitions = []
		# first get the partitions defined for the switch
		for row in interface_data:
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

			# parse out partitions
			for part in partitions.split(','):
				try:
					# error or ignore?
					partition = '0x%04d' % int(part)
				except (ValueError, IndexError):
					continue

				good_partitions.append(partition)

			break

		return fabric, good_partitions


	def get_partition_members(self, fabric, interface_data):
		# get the appliance for each host
		lst_host_appliances = dict(
			(k, next(v)) for k, v in groupby(self.owner.call('list.host'), itemgetter('host'))
		)

		partition_data = s.partitions.copy()

		# for backend nodes, we're looking for 'ibpartition' specified in the 'options' field of ibN ifaces
		for row in interface_data:
			iface = IfInfo(*iface_getter(row))

			if lst_host_appliances[iface.host]['appliance'] == 'switch':
				# ib switches don't have their own ib interfaces listed
				# so this is probably the ethernet mgmt port
				continue

			if not iface.interface.startswith(fabric):
				# not an ib iface or not on the right fabric
				continue
			if not iface.mac:
				# no guid
				continue
			mac = iface.mac[-23:].lower()

			if iface.options is None:
				# no partition info set
				continue
			if 'ibpartition=' not in iface.options:
				# no partition info set
				continue

			opts = shlex.split(iface.options)

			# we already know 'ibpartition=' is present
			_, partitions = next(opt.split('=') for opt in opts if opt.startswith('ibpartition='))

			# parse out partitions
			for part in partitions.split(','):
				# check if membership is specified... default to limited
				membership = 'limited'
				try:
					# format is "NNNN:f"
					part, membership = part.split(':')

					if membership[0].lower() == 'f':
						membership = 'full'
				except ValueError:
					continue

				# validate partition name
				try:
					partition = '0x%04d' % int(part)
				except (ValueError, IndexError):
					if partition.lower() == 'default':
						partition = 'Default'
					else:
						# error or ignore?
						continue

				good_partitions.append(partition, mac, membership)

		
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

		try:
			pubkey = open('/root/.ssh/id_rsa.pub').read()
			s.ssh_copy_id(pubkey.strip())
		except FileNotFoundError:
			pass

		if not s.subnet_manager:
			return

		lst_host_iface = self.owner.call('list.host.interface')

		fabric, good_partitions = get_needed_partitions(switch, lst_host_iface)

		for partition in good_partitions:
			if partition in s.partitions:
				continue

			try:
				s.add_partition(partition, int(partition, 16))
			except SwitchException as e:
				msg = f'Error while attempting to add partition "{partition}" to {switch}:\n{e}'
				raise CommandError(self.owner, msg)

		unused_partitions = set(s.partitions).difference(good_partitions)
		for part in unused_partitions:
			s.del_partition(part)

		if not fabric:
			raise CommandError(self.owner, 'no fabric specified')

		get_partition_members(fabric, lst_host_iface)
		
		if partition not in partition_data:
			# skip adding members for non-existant partitions
			continue

		if mac in partition_data[partition]['guids']:
			# don't add the same guid twice

		s.add_partition_member(partition, mac, membership=membership)

		
		# if the only partition is 'Default', everyone should be a full member
		if list(s.partitions.keys()) == ['Default']:
			for mac in macs_for_default:
				s.add_partition_member('Default', mac[-23:], membership='limited')
