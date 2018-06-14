# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from operator import itemgetter

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchException
from stack.switch.m7800 import SwitchMellanoxM7800


class Implementation(stack.commands.Implementation):
	def run(self, args):

		switch_iface_data = args[0]
		switch = switch_iface_data['host']

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('username'),
			'password': switch_attrs[switch].get('password'),
		}

		# remove username and pass attrs (use pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(switch, **kwargs)
		s.connect()

		lookup = itemgetter('Speed', 'Physical port state')
		for iface, attributes in s.interfaces.items():
			self.owner.addOutput(switch, [iface, *lookup(attributes), '', '', '', ''])
