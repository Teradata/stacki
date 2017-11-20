# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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


class Command(stack.commands.list.host.command):
	"""
	List the static routes that are assigned to a host.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='list host route compute-0-0'>
	List the static routes assigned to compute-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		for host in self.getHostnames(args):
			routes = self.db.getHostRoutes(host, 1)

			for network in sorted(routes.keys()):
				(netmask, gateway, interface, source) = routes[network]
				self.addOutput(host,
					(network, netmask, gateway,	source))

		self.endOutput(header=['host', 
			'network', 'netmask', 'gateway', 'source' ],
			trimOwner=0)

