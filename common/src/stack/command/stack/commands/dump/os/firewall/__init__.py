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
# Revision 1.1  2010/05/07 18:27:43  bruno
# closer
#
#

import stack.commands
import stack.commands.dump
import stack.commands.dump.firewall


class Command(stack.commands.OSArgumentProcessor,
	stack.commands.dump.firewall.command):
	"""
	"""

	def run(self, params, args):
		for os in self.getOSNames(args):

			rows = self.db.execute("""select tabletype, name, insubnet,
				outsubnet, service, protocol, chain, action, flags,
				comment from os_firewall where os = '%s' """
				% os)

			if rows > 0:
				self.dump_firewall('os', os)

