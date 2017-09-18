# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.3  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.2  2009/04/23 17:12:29  bruno
# cleanup 'rocks remove host' command
#
# Revision 1.1  2009/03/13 22:19:56  mjk
# - route commands done
# - cleanup of stack.host plugins
#
# Revision 1.2  2009/03/06 21:28:12  bruno
# need to look at node_attributes table.
#
# Revision 1.1  2008/12/18 20:01:33  mjk
# attribute commands
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'attr'

	def run(self, hosts):
		for host in hosts:
			self.owner.db.execute("""delete from attributes
				where scope="host" and 
				scopeid=(select id from nodes where name = '%s')""" %
				host)

