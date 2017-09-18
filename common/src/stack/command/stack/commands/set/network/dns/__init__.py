# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands.set.network


class Command(stack.commands.set.network.command):
	"""
	Enables or Disables DNS for one of more networks.
	
	If DNS is enabled for a network then all known hosts on that network
	will have their hostnames and IP addresses in a DNS server running
	on the Frontend.  This will serve both forward and reverse lookups.

	<arg type='string' name='network' optional='1' repeat='1'> 
	The names of zero of more networks. If no network is specified
	the DNS is set for all existing networks.
	</arg>
	
	<param type='boolean' name='dns' optional='0'>
	Set to True to enable DNS for the given networks.
	</param>
	
	<example cmd='set network dns private dns=false'>
	Disables DNS on the "private" network.
	</example>
	"""
		
	def run(self, params, args):

		(networks, dns) = self.fillSetNetworkParams(args, 'dns')
		dns = self.str2bool(dns)
		 
		for network in networks:
			self.db.execute("""
				update subnets set dns=%s where
				subnets.name='%s'
				""" % (dns, network))

