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

