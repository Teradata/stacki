# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):
	def run(self, args):

		# switch hostname
		switch, = args

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('switch_username'),
			'password': switch_attrs[switch].get('switch_password'),
		}

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		ib_switch = SwitchMellanoxM7800(switch, **kwargs)
		ib_switch.connect()

		# Get all partitions on ib switch
		partitions = ib_switch.partitions

		for partition, part_values in partitions.items():
			ipoib = part_values['ipoib']
			defmember = part_values['defmember']

			if part_values['pkey']:
				pkey = '0x{0:04x}'.format(part_values['pkey'])
			else:
				pkey = part_values['pkey']
			if part_values['defmember']:
				self.owner.addOutput(switch, [partition, pkey, f'ipoib={ipoib},defmember={defmember}'])
			else:
				self.owner.addOutput(switch, [partition, pkey, f'ipoib={ipoib}'])
