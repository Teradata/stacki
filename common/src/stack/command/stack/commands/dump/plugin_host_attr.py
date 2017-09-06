# $Id$
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.3  2009/05/01 19:06:56  mjk
# chimi con queso
#
# Revision 1.2  2009/03/13 21:10:49  mjk
# - added dump route commands
#
# Revision 1.1  2008/12/23 00:14:05  mjk
# - moved build and eval of cond strings into cond.py
# - added dump appliance,host attrs (and plugins)
# - cond values are typed (bool, int, float, string)
# - everything works for client nodes
# - random 80 col fixes in code (and CVS logs)
#

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host-attr'
		
	def requires(self):
		return [ 'host' ]
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.host.attr', []))
		

