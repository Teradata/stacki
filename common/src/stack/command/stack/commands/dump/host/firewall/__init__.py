# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:53  bruno
# star power for gb
#
# Revision 1.3  2010/05/13 21:50:14  bruno
# almost there
#
# Revision 1.2  2010/05/07 18:27:43  bruno
# closer
#
# Revision 1.1  2010/04/30 22:07:16  bruno
# first pass at the firewall commands. we can do global and host level
# rules, that is, we can add, remove, open (calls add), close (also calls add),
# list and dump the global rules and the host-specific rules.
#

import stack.commands
import stack.commands.dump
import stack.commands.dump.firewall


class Command(stack.commands.dump.host.command,
	stack.commands.dump.firewall.command):
	"""
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			dumpname = self.dumpHostname(host)

			rows = self.db.execute("""select tabletype, name, insubnet,
				outsubnet, service, protocol, action, chain, flags,
				comment from node_firewall where
				node = (select id from nodes where name = '%s')
				""" % host)

			if rows > 0:
				self.dump_firewall('host', dumpname)

