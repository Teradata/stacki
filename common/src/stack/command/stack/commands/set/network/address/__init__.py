# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import ipaddress
import stack.commands.set.network
from stack.exception import ArgUnique, CommandError


class Command(stack.commands.set.network.command):
	"""
	Sets the network address of a network.

	<arg type='string' name='network' optional='0' repeat='0'>
	The name of the network.
	</arg>
	
	<param type='string' name='address' optional='0'>
	Address that the named network should have.
	</param>
	
	<example cmd='set network address ipmi address=192.168.10.0'>
	Sets the "ipmi" network address to 192.168.10.0.
	</example>
	"""
		
	def run(self, params, args):

		(networks, address) = self.fillSetNetworkParams(args, 'address')
		if len(networks) > 1:
			raise ArgUnique(self, 'network')

		network = networks[0]
		rows = self.db.select("""
			mask from subnets where name='%s'
			""" % network)

		if not rows:
			raise CommandError(self, 'network "%s" doesn\'t exist' % name)

		mask = rows[0][0]
		try:
			if ipaddress.IPv4Network(u"%s/%s" % (address, mask)):
				pass
		except:
			msg = '%s/%s is not a valid network address and subnet mask combination'
			raise CommandError(self, msg % (address, mask))
					
		for network in networks:
			self.db.execute("""
				update subnets set address='%s' where
				subnets.name='%s'
				""" % (address, network))

