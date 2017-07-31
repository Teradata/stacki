# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.5  2010/10/28 21:11:36  bruno
# no need to protect the firewall dump output with CDATA, the restore roll
# already does that and embedded CDATA statements is an XML error.
#
# Revision 1.4  2010/09/07 23:52:52  bruno
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
#

import stack.commands

class command(stack.commands.NetworkArgumentProcessor, 
	stack.commands.dump.command):

	def dump_firewall(self, level='', id=''):
		for t, n, i, o, s, p, a, c, f, cmt in self.db.fetchall():
			cmd = []
			if i == 0:
				name = 'all'
			else:
				name = self.getNetworkName(i)
			if name:
				cmd.append('network=%s' % name)

			if o == 0:
				name = 'all'
			else:
				name = self.getNetworkName(o)
			if name:
				cmd.append('output-network=%s' % name)
			if t:
				cmd.append('table=%s' % t)
			if n:
				cmd.append('rulename=%s' % n)
			if s:
				cmd.append('service="%s"' % s)
			if p:
				cmd.append('protocol="%s"' % p)
			if a:
				cmd.append('action="%s"' % a)
			if c:
				cmd.append('chain="%s"' % c)
			if f:
				cmd.append('flags="%s"' % f)
			if cmt:
				cmd.append('comment="%s"' % cmt)

			self.dump('add %s firewall %s %s' % (level, id,
				' '.join(cmd)))


class Command(command):
	"""
	Dump the global firewall services and rules
	"""
	def run(self, params, args):
		self.db.execute("""select tabletype, name, insubnet,
			outsubnet, service, protocol, action, chain, flags,
			comment from global_firewall""")

		self.dump_firewall()

