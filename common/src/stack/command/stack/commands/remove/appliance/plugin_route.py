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
# Revision 1.3  2010/07/19 18:30:51  anoop
# Bug fix
# "rocks remove appliance" runs "rocks remove appliance route" plugin
# without any args. "remove appliance route" cannot be run without args,
# and "rocks remove appliance" fails. So now instead of calling the command,
# the plugin runs sql directly to remove appropriate entries from the
# appliance routes table;
#
# Revision 1.2  2009/05/01 19:06:59  mjk
# chimi con queso
#
# Revision 1.1  2009/03/13 22:19:55  mjk
# - route commands done
# - cleanup of stack.host plugins
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'route'

	def run(self, appliance):
		self.owner.db.execute("""
			delete from appliance_routes
			where appliance=(select id from appliances where name=%s)
		""", (appliance,))
