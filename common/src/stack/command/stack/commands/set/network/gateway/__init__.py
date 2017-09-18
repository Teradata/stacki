# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
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
					
		for network in networks:
			self.db.execute("""
				update subnets set gateway='%s' where
				subnets.name='%s'
				""" % (gateway, network))

