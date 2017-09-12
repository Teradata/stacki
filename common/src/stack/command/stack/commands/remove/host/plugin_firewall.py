# $Id$
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.3  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.2  2010/05/14 23:25:52  bruno
# cleanup remove plugins for the firewall tables
#
# Revision 1.1  2010/05/11 22:29:21  bruno
# plugin for removing host-specific firewall rules when a host is removed
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'firewall'

	def run(self, hosts):
		#
		# since we are not setting any command line parameters, we
		# just need to remove all rows in the database that match this
		# host
		#
		for host in hosts:
			self.db.execute("""delete from node_firewall where
				node = (select id from nodes where
				name = '%s')""" % host)	

