# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
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
	Dump the set of firewall rules for an os

	<arg optional='1' type='string' name='os' repeat='1'>
	Zero or more OS names
	</arg>

	<example cmd='dump os firewall redhat'>
	Dump firewall rules for redhat OS.
	</example>
	"""

	def run(self, params, args):
		for os in self.getOSNames(args):

			rows = self.db.execute("""select tabletype, name, insubnet,
				outsubnet, service, protocol, chain, action, flags,
				comment from os_firewall where os = '%s' """
				% os)

			if rows > 0:
				self.dump_firewall('os', os)

