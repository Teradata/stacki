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
# Revision 1.1  2009/12/16 18:29:39  bruno
# need to save the boot action in the restore roll
#
#

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host-boot'
		
	def requires(self):
		return [ 'host', 'interface' ]
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.host.boot', []))
		

