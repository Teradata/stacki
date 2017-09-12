# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:52:53  bruno
# star power for gb
#
# Revision 1.1  2009/12/16 18:29:40  bruno
# need to save the boot action in the restore roll
#
#

import stack.commands


class Command(stack.commands.dump.host.command):
	"""
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			rows = self.db.execute("""select b.action from 
				nodes n, boot b where n.id = b.node and
				n.name = '%s' """ % host)

			if rows == 1:
				action, = self.db.fetchone()
				self.dump('set host boot %s action=%s'
					% (self.dumpHostname(host), action))

