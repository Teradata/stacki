# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
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
	Dump the set of firewall rules for appliances.

	<arg optional='1' type='string' name='appliance'>
	Name of appliance
	</arg>

	<example cmd='dump appliance firewall backend'>
	List the firewall rules for backend appliances
	</example>
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

