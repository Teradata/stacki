# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.list.command):
	"""
	List the global routes.

	<example cmd='list route'>
	Lists all the global routes for this cluster.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		routes = self.db.select("""network, netmask, gateway, subnet, interface from global_routes""")
		for network, netmask, gateway, subnet_id, interface in routes:
			if subnet_id:
				subnet_name = self.db.select("""name from
					subnets where id = %s""", [subnet_id])[0][0]
			else:
				subnet_name = None
			# list this as a None rather than a string that says NULL
			if interface == 'NULL':
				interface = None
			self.addOutput(network, (netmask, gateway, subnet_name, interface))

		self.endOutput(header=['network', 'netmask', 'gateway', 'subnet', 'interface' ],
			trimOwner=0)
