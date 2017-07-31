# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:53  bruno
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
# Revision 1.1  2009/03/13 21:10:50  mjk
# - added dump route commands
#

import stack.commands

class Command(stack.commands.dump.command):
	"""
	Dump the set of routes
	"""

	def run(self, params, args):
		self.db.execute("""select network, netmask, gateway, subnet
			from global_routes""")

		for n, m, g, s in self.db.fetchall():
			if s:
				rows = self.db.execute("""select name from
					subnets where id = %s""" % s)
				if rows == 1:
					g, = self.db.fetchone()

			self.dump('add route %s %s netmask=%s' % (n, g, m))

