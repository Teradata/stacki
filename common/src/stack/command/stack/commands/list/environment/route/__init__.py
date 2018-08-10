# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:56  bruno
# star power for gb
#
# Revision 1.3  2010/05/20 00:31:45  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
# Revision 1.2  2009/05/01 19:06:59  mjk
# chimi con queso
#
# Revision 1.1  2009/03/13 20:34:19  mjk
# - added list.appliance.route
# - added list.os.route
#

import stack.commands


class Command(stack.commands.list.environment.command):
	"""
	List the routes for one or more environments

	<arg optional='1' type='string' name='environment' repeat='1'>
	Zero, one or more environments.
	</arg>

	"""

	def run(self, params, args):

		self.beginOutput()

		for environment in self.getEnvironmentNames(args):
			((env, ), ) = self.db.select("""id FROM environments WHERE name=%s""", environment)

			self.db.execute("""select network, netmask, gateway,
				subnet from environment_routes where environment='%s'""" % env)

			for (network, netmask, gateway, subnet) in self.db.fetchall():
				if subnet:
					rows = self.db.execute("""select name
						from subnets where id = %s"""
						% subnet)
					if rows == 1:
						gateway, = self.db.fetchone()

				self.addOutput(environment, (network, netmask, gateway))

		self.endOutput(header=['environment', 'network', 'netmask', 'gateway' ], trimOwner=0)

