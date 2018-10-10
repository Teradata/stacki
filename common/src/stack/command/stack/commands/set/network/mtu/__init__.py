# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network


class Command(stack.commands.set.network.command):
	"""
	Sets the MTU for one or more networks.

	<arg type='string' name='network' optional='0' repeat='1'>
	The names of one or more networks.
	</arg>

	<param type='string' name='mtu' optional='0'>
	MTU value the networks should have.
	</param>

	<example cmd='set network mtu fat mtu=9000'>
	Sets the "fat" network to jumbo frames.
	</example>
	"""

	def run(self, params, args):

		(networks, mtu) = self.fillSetNetworkParams(args, 'mtu')

		for network in networks:
			self.db.execute(
				'update subnets set mtu=%s where name=%s',
				(mtu, network)
			)
