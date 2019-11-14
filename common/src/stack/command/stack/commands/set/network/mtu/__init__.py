# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network
from stack.exception import *


class Command(stack.commands.set.network.command):
	"""
	Sets the MTU for one or more networks.

	<arg type='string' name='network' optional='0' repeat='1'>
	The names of one or more networks.
	</arg>

	<param type='integer' name='mtu' optional='0'>
	MTU value the networks should have. This can
	take an empty string to unset the MTU
	</param>

	<example cmd='set network mtu fat mtu=9000'>
	Sets the "fat" network to jumbo frames.
	</example>

	<example cmd='set network mtu IB mtu='>
	Unsets the MTU for the "IB" network.
	</example>
	"""

	def run(self, params, args):

		(networks, mtu) = self.fillSetNetworkParams(args, 'mtu')

		if not mtu:
			mtu = None
		else:
			try:
				mtu = int(mtu)
			except:
				raise ParamType(self, 'mtu', 'integer')

		for network in networks:
			self.db.execute(
				'update subnets set mtu=%s where name=%s',
				(mtu, network)
			)
