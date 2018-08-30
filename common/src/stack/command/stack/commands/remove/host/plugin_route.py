# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.3  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.2  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.1  2009/03/13 22:19:56  mjk
# - route commands done
# - cleanup of stack.host plugins
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'route'

	def run(self, hosts):
		for host in hosts:
			self.owner.command('remove.host.route', [host, 'address=*'])
