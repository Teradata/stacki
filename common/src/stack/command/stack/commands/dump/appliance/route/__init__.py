# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.3  2010/05/20 00:31:44  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
# Revision 1.2  2009/05/01 19:06:56  mjk
# chimi con queso
#
# Revision 1.1  2009/03/13 21:10:49  mjk
# - added dump route commands
#

import stack.commands


class Command(stack.commands.dump.appliance.command):
	"""
	"""

	def run(self, params, args):
		for app in self.getApplianceNames(args):
			self.db.execute("""
				select r.network, r.netmask, r.gateway,
				r.subnet from appliance_routes r, appliances a
				where r.appliance=a.id and a.name='%s'""" % app)

			for n, m, g, s in self.db.fetchall():
				if s:
					rows = self.db.execute("""select name
						from subnets where id = %s"""
						% s)
					if rows == 1:
						g, = self.db.fetchone()

				self.dump('add appliance route '
					'%s %s %s netmask=%s' % (app, n, g, m))

