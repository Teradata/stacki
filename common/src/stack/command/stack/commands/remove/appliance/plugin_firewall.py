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
# Revision 1.2  2010/05/14 23:25:52  bruno
# cleanup remove plugins for the firewall tables
#
# Revision 1.1  2010/05/07 18:27:43  bruno
# closer
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'firewall'

	def run(self, appliance):
		#
		# since we are not setting any parameters, we just need to
		# remove all rows in the database that have this appliance
		# type
		#
		self.db.execute("""delete from appliance_firewall where
			appliance = (select id from appliances where
			name = '%s')""" % appliance)	
