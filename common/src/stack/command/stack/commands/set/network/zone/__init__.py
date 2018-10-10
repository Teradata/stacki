# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network
from stack.exception import ArgUnique


class Command(stack.commands.set.network.command):
	"""
	Sets the DNS zone (domain name) for a network.

	<arg type='string' name='network' optional='0' repeat='0'>
	The name of the network.
	</arg>

	<param type='string' name='zone' optional='0'>
	Zone that the named network should have.
	</param>

	<example cmd='set network zone ipmi zone=ipmi'>
	Sets the "ipmi" network zone to "ipmi".
	</example>
	"""

	def run(self, params, args):

		(networks, zone) = self.fillSetNetworkParams(args, 'zone')
		if len(networks) > 1:
			raise ArgUnique(self, 'network')

		network = networks[0]

		self.db.execute(
			'update subnets set zone=%s where name=%s',
			(zone, network)
		)
