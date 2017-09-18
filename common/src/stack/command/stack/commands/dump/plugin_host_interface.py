# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.9  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.8  2009/05/01 19:06:56  mjk
# chimi con queso
#
# Revision 1.7  2009/03/13 21:10:49  mjk
# - added dump route commands
#
# Revision 1.6  2008/10/18 00:55:49  mjk
# copyright 5.1
#
# Revision 1.5  2008/07/22 00:34:40  bruno
# first whack at vlan support
#
# Revision 1.4  2008/04/29 21:28:38  bruno
# dump the network info
#
# Revision 1.3  2008/03/06 23:41:36  mjk
# copyright storm on
#
# Revision 1.2  2007/06/19 16:42:41  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.1  2007/06/12 19:56:18  mjk
# added lost plugins
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'interface'
		
	def requires(self):
		return [ 'host', 'network', 'vlan' ]
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.host.interface',
			[]))
		

