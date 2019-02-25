# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import UsageError, ArgUnique, CommandError
from stack.util import flatten

class Command(stack.commands.list.host.command):
	"""
	Lists the aliases for a host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, aliases
	for all the known hosts is listed.
	</arg>

	<param type='string' name='interface' optional='1'>
	Interface of host.
	</param>

	<example cmd='list host alias backend-0-0 interface=eth0'>
	List the aliases for backend-0-0 on interface "eth0".
	</example>
	"""

	def run(self, params, args):
		if 'host' in params or 'hosts' in params:
			raise UsageError(self, "Incorrect usage.")

		(interface, ) = self.fillParams([
			('interface', None)
		])

		self.beginOutput()
		for host in self.getHostnames(args):
			if interface == None:
				devices = flatten(self.db.select("""
					device from networks
					where node = (select id from nodes where name = %s)
					""", (host,)
				))
			else:
				devices = (interface,)

			for device in devices:
				for alias, in self.db.select("""
					name from aliases
					where network = (
						select id from networks
						where node = (select id from nodes where name = %s)
						and device = %s
					)""", (host, device)
				):
					self.addOutput(host, (alias, device))

		self.endOutput(header=['host', 'alias', 'interface'], trimOwner=False)
