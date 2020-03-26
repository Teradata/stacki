# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.commands import NetworkArgProcessor
from stack.exception import ArgRequired, CommandError

class Command(NetworkArgProcessor, stack.commands.remove.command):
	"""
	Remove network definition from the system. If there are still nodes
	defined in the database that are assigned to the network name you
	are trying to remove, the command will not remove the network
	definition and print a message saying it cannot remove the network.

	<arg type='string' name='network' repeat='1'>
	One or more network names.
	</arg>

	<example cmd='remove network private'>
	Remove network info for the network named 'private'.
	</example>
	"""

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'network')

		networks = self.getNetworkNames(args)

		# Get a list of networks currently attached to host interfaces
		in_use = {
			interface['network']
			for interface in self.call('list.host.interface')
		}

		# See if any are in use
		for network in networks:
			if network in in_use:
				raise CommandError(self, f'network "{network}" in use')

		# Safe to delete them
		for network in networks:
			self.db.execute('delete from subnets where name=%s', (network,))
