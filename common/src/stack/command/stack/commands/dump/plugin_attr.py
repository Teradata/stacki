# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
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
# Revision 1.1  2009/01/08 23:36:01  mjk
# - rsh edge is conditional (no more uncomment crap)
# - add global_attribute commands (list, set, remove, dump)
# - attributes are XML entities for kpp pass (both pass1 and pass2)
# - attributes are XML entities for kgen pass (not used right now - may go away)
# - some node are now interface=public
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'attr'
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.attr', []))
		

