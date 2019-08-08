# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800
from collections import namedtuple

class Implementation(stack.commands.Implementation):
	def run(self, args):

		# switch hostname
		switch, = args
		switch_attrs = self.owner.getHostAttrDict(switch)
		kwargs = {
			'username': switch_attrs[switch].get('switch_username'),
			'password': switch_attrs[switch].get('switch_password'),
		}
		part_info = namedtuple('ib_part', 'part pkey options')
		part_list = []

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		ib_switch = SwitchMellanoxM7800(switch, **kwargs)
		ib_switch.connect()

		# Get all partitions on ib switch
		partitions = ib_switch.partitions

		for partition, part_values in partitions.items():
			options = [f'ipoib=part_values["ipoib"]']
			pkey = part_values['pkey']

			if defmember:
				options.append(f'defmember=part_values["defmember"]')

			if pkey:
				pkey = '0x{0:04x}'.format(pkey)

			partition = part_info(partition, pkey, ','.join(options))
			part_list.append(partition)

		return part_list
