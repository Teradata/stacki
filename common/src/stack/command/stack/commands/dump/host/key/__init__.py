# @copyright@
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.dump.host.command):
	"""
	Dump the public keys for hosts.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='dump host key stacki-01'>
	Dumps the public keys for stacki-01
	</example>
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			self.db.execute("""select public_key from
				public_keys where node = (select id from
				host_view where name = '%s') """ % host)

			for k, in self.db.fetchall():
				self.dump('add host key %s key="%s"'
					% (self.dumpHostname(host), k))

