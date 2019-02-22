# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network
from stack.exception import ArgUnique, CommandError


class Command(stack.commands.set.network.command):
	"""
	Sets the network name of a network.

	<arg type='string' name='network' optional='0' repeat='0'>
	The name of the network.
	</arg>

	<param type='string' name='name' optional='0'>
	Name that the named network should have.
	</param>

	<example cmd='set network name private name=data'>
	Changes the name of the "private" network to "data".
	</example>
	"""

	def run(self, params, args):

		(networks, name) = self.fillSetNetworkParams(args, 'name')
		if len(networks) > 1:
			raise ArgUnique(self, 'network')

		if ' ' in name:
			raise CommandError(self, 'network name must not contain a space')

		network = networks[0]

		self.db.execute(
			'update subnets set name=%s where name=%s',
			(name, network)
		)
