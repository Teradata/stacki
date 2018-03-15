# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.6  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.5  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.4  2009/03/13 22:19:56  mjk
# - route commands done
# - cleanup of stack.host plugins
#
# Revision 1.3  2008/10/18 00:55:55  mjk
# copyright 5.1
#
# Revision 1.2  2008/03/06 23:41:38  mjk
# copyright storm on
#
# Revision 1.1  2008/02/01 20:52:27  bruno
# use plugins to support removing all database entries for a host.
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'bootflags'

	def run(self, hosts):
		pass
# We don't use bootflags anymore
# Do we?
#		self.owner.command('remove.host.bootflags', hosts )
		
