# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network


class Command(stack.commands.set.network.command):
	"""
	Sets the MTU for one or more networks.

	<arg type='string' name='network' optional='1' repeat='1'> 
	The names of zero of more networks. If no network is specified
	the MTU is set for all existing networks.
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
			self.db.execute("""
				update subnets set mtu='%s' where
				subnets.name='%s'
				""" % (mtu, network))

