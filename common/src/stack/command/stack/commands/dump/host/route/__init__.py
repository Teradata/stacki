# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands
from stack.exception import *


class Command(stack.commands.dump.host.command):
	"""
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			self.db.execute("""
				select r.network, r.netmask, r.gateway,
				r.subnet from node_routes r, nodes n where
				r.node=n.id and n.name='%s'""" % host)

			for n, m, g, s in self.db.fetchall():
				if s:
					rows = self.db.execute("""select name
						from subnets where id = %s"""
						% s)
					if rows == 1:
						g, = self.db.fetchone()

				self.dump('add host route %s %s %s netmask=%s'
					% (self.dumpHostname(host), n, g, m))

