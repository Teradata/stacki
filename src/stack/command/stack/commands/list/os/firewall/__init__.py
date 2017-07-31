# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:56  bruno
# star power for gb
#
# Revision 1.3  2010/05/11 22:28:16  bruno
# more tweaks
#
# Revision 1.2  2010/05/07 23:13:32  bruno
# clean up the help info for the firewall commands
#
# Revision 1.1  2010/05/05 18:15:21  bruno
# all firewall list commands are done
#
#

import stack.commands

class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.list.os.command):
	"""
	List the firewall rules for an OS.

	<arg optional='1' type='string' name='os' repeat='1'>
	Zero, one or more OS names. If no OS names are supplied, the firewall
	rules for all OSes are listed.
	</arg>
	"""

	def run(self, params, args):
		self.beginOutput()

		for os in self.getOSNames(args):

			self.db.execute("""select insubnet, outsubnet,
				service, protocol, chain, action, flags,
				comment, name, tabletype from os_firewall
				where os = '%s' """ % os)

			for i, o, s, p, c, a, f, cmt, n, tt in self.db.fetchall():
				network = self.getNetworkName(i)
				output_network = self.getNetworkName(o)

				self.addOutput(os, (n, tt, s, p, c, a, network,
					output_network, f))

		self.endOutput(header=['os', 'name', 'table', 'service',
			'protocol', 'chain', 'action', 'network',
			'output-network', 'flags', 'comment' ], trimOwner=0)

