# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
import stack.commands
from stack import api
from stack.switch.m7800 import SwitchMellanoxM7800
from collections import namedtuple

class Implementation(stack.commands.Implementation):
	def get_host_interface_by_mac(self, mac):
		# Return the host name, interface name, and address
		# if a given mac belongs to a host in the database
		host = ''
		interface_name = ''
		address = ''
		for interface in api.Call('list host interface'):
			# If a mac addresses matches what's in the database
			# Get it's host name and interface name
			if interface['mac'] and mac.lower() in interface['mac'].lower():
				found_mac = interface['mac']
				host = interface.get('host', '')
				address = interface.get('ip', '')
				interface_name = interface.get('interface', '')
		return {'host_name': host, 'interface_name': interface_name}

	def run(self, args):

		# switch hostname
		switch, = args

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('switch_username'),
			'password': switch_attrs[switch].get('switch_password'),
		}
		partition_info = {}
		part_member = namedtuple('member', 'host interface guid partition membership pkey options')

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		ib_switch = SwitchMellanoxM7800(switch, **kwargs)
		ib_switch.connect()


		# Get all partitions on ib switch
		partitions = ib_switch.partitions

		for partition, part_values in partitions.items():
			members = part_values['guids']
			member_list = []

			# Go through each partition member and output it
			for guid, membership in members.items():
				host = self.get_host_interface_by_mac(guid)
				pkey = part_values['pkey']
				ipoib = part_values['ipoib']
				defmember = part_values['defmember']
				options = []

				# Format partition key
				if pkey:
					pkey = '0x{0:04x}'.format(pkey)

				if ipoib:
					options.append(f'ipoib={ipoib}')

				if defmember:
					options.append(f'defmember={defmember}')

				member = part_member(host['host_name'], host['interface_name'], guid, partition, membership, pkey, ','.join(options))
				member_list.append(member)

			partition_info[partition] = member_list

		return partition_info
