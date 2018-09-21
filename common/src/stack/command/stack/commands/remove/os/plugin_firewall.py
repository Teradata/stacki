# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.3  2010/09/07 23:52:58  bruno
# star power for gb
#
# Revision 1.2  2010/05/14 23:25:52  bruno
# cleanup remove plugins for the firewall tables
#
# Revision 1.1  2010/05/11 22:29:00  bruno
# added plugins for all 'remove os' commands
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'firewall'

	def run(self, os):
		self.db.execute('delete from os_firewall where os=%s', (os,))
