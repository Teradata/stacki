# $Id$
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.3  2011/01/11 17:35:19  bruno
# dump the host public keys
#
# Revision 1.2  2010/09/07 23:52:53  bruno
# star power for gb
#
# Revision 1.1  2010/06/15 19:35:43  bruno
# commands to:
#  - manage public keys
#  - start/stop a service
#
#

import stack.commands

class Command(stack.commands.dump.host.command):
	"""
	Dump the public keys for hosts.
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			self.db.execute("""select public_key from
				public_keys where node = (select id from
				nodes where name = '%s') """ % host)

			for k, in self.db.fetchall():
				self.dump('add host key %s key="%s"'
					% (self.dumpHostname(host), k))

