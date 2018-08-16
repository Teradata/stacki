# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
	
	<example cmd='list host route backend-0-0'>
	List the static routes assigned to backend-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		for host in self.getHostnames(args):
			routes = self.db.getHostRoutes(host, 1)

			for network in sorted(routes.keys()):
				(netmask, gateway, interface, subnet_id, source) = routes[network]

				if subnet_id:
					# resolve the subnet id
					subnet_name = self.db.select("""name from subnets where id=%s""", [subnet_id])[0][0]
				else:
					subnet_name = None

				self.addOutput(host,
					(network, netmask, gateway, subnet_name, interface, source))

		self.endOutput(header=['host', 'network', 'netmask', 'gateway',
					'subnet', 'interface', 'source' ],trimOwner=0)
