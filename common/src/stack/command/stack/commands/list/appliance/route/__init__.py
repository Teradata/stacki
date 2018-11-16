# @copyright@
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.list.appliance.command):
	"""
	List the routes for a given appliance type.

	<arg optional='1' type='string' name='appliance' repeat='1'>
	Zero, one or more appliance names. If no appliance names are supplied,
	the routes for all the appliances are listed.
	</arg>
	"""

	def run(self, params, args):

		self.beginOutput()

		for app in self.getApplianceNames(args):
			routes = self.db.select("""r.network, r.netmask, r.gateway,
				r.subnet, r.interface from appliance_routes r, appliances a
				where r.appliance=a.id and a.name=%s""", app)
			for network, netmask, gateway, subnet, interface in routes:
				if subnet:
					subnet_name = self.db.select("""name from subnets where id=%s""",
								[subnet])[0][0]
				else:
					subnet_name = None
				if interface == 'NULL':
					interface = None
				self.addOutput(app, (network, netmask, gateway, subnet_name, interface))

		self.endOutput(header=['appliance', 'network', 'netmask', 'gateway',
				'subnet', 'interface' ], trimOwner=0)
