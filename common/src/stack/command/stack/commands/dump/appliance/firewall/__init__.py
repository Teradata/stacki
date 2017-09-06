# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.1  2010/05/07 18:27:43  bruno
# closer
#
#

import stack.commands
import stack.commands.dump
import stack.commands.dump.firewall

class Command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.dump.firewall.command):
	"""
	"""

	def run(self, params, args):
		for app in self.getApplianceNames(args):
			rows = self.db.execute("""select tabletype, name, insubnet,
				outsubnet, service, protocol, chain, action, flags,
				comment from appliance_firewall where
				appliance = (select id from appliances where
				name = '%s')""" % app)

			if rows > 0:
				self.dump_firewall('appliance', app)

