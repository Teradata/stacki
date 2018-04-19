# @copyright@
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
import stack.commands.dump
import stack.commands.dump.firewall


class Command(stack.commands.dump.host.command,
	stack.commands.dump.firewall.command):
	"""
	Dump the set of host firewall rules

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='dump host firewall'>
	Dump the set of all host firewall rules
	</example>
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			dumpname = self.dumpHostname(host)

			rows = self.db.execute("""select tabletype, name, insubnet,
				outsubnet, service, protocol, action, chain, flags,
				comment from node_firewall where
				node = (select id from host_view where name = '%s')
				""" % host)

			if rows > 0:
				self.dump_firewall('host', dumpname)

