# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.remove.command):
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
			
		# use the default argument handling but protect the user
		# from ever deleting networks (subnets table) that are
		# in use.  More general than just protecting the 'public'
		# and 'private' networks.
		
		networks = self.getNetworkNames(args)
		
		for network in networks:
			rows = self.db.execute("""select * from 
				networks net, subnets sub where
				net.subnet=sub.id and 
				sub.name='%s'""" % network)

			if rows > 0:
				raise CommandError(self, 'cannot remove ' +
					'"%s" ' % (network) +
					'network. There are nodes still ' +
					'associated with it.')
					
		for network in networks:
			self.db.execute("""delete from subnets where 
				name='%s'""" % network)

