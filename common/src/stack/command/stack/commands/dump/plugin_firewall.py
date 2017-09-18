# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.3  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.2  2010/05/20 00:31:44  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
# Revision 1.1  2010/04/30 22:07:16  bruno
# first pass at the firewall commands. we can do global and host level
# rules, that is, we can add, remove, open (calls add), close (also calls add),
# list and dump the global rules and the host-specific rules.
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'firewall'

	def requires(self):
		return [ 'network' ]
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.firewall', []))
		

