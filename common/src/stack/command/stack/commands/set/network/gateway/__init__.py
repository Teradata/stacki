# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network
from stack.exception import ArgUnique


class Command(stack.commands.set.network.command):
	"""
	Sets the network gateway of a network.

	<arg type='string' name='network' optional='0' repeat='0'>
	The name of the network.
	</arg>

	<param type='string' name='gateway' optional='0'>
	Gateway that the named network should have.
	</param>

	<example cmd='set network gateway ipmi gateway=192.168.10.1'>
	Sets the "ipmi" network gateway to 192.168.10.1.
	</example>
	"""

	def run(self, params, args):

		(networks, gateway) = self.fillSetNetworkParams(args, 'gateway')
		if len(networks) > 1:
			raise ArgUnique(self, 'network')

		network = networks[0]

		self.db.execute(
			'update subnets set gateway=%s where name=%s',
			(gateway, network)
		)
