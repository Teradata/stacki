# @copyright@
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
			rows = self.db.execute("""select b.action from 
				host_view hv, boot b where hv.id = b.node and
				hv.name = '%s' """ % host)

			if rows == 1:
				action, = self.db.fetchone()
				self.dump('set host boot %s action=%s'
					% (self.dumpHostname(host), action))

