# $Id$
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.1  2010/05/20 00:31:44  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'os-route'
		
	def requires(self):
		return [ 'os', 'network' ]
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.os.route', 
			[]))
		

