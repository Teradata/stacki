# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:54  bruno
# star power for gb
#
# Revision 1.3  2010/05/20 00:31:45  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
# Revision 1.2  2009/05/01 19:06:57  mjk
# chimi con queso
#
# Revision 1.1  2009/03/13 20:34:19  mjk
# - added list.appliance.route
# - added list.os.route
#

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
			self.db.execute("""
				select r.network, r.netmask, r.gateway,
				r.subnet from appliance_routes r, appliances a
				where r.appliance=a.id and a.name='%s'""" % app)

			for network, netmask, gateway, subnet in \
				self.db.fetchall():

				if subnet:
					rows = self.db.execute("""select name
						from subnets where id = %s"""
						% subnet)
					if rows == 1:
						gateway, = self.db.fetchone()

				self.addOutput(app, (network, netmask, gateway))

		self.endOutput(header=['appliance', 'network', 
			'netmask', 'gateway' ], trimOwner=0)

