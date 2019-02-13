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


class Command(stack.commands.list.host.command):
	"""
	List the public keys for hosts.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied,
	information for all hosts will be listed.
	</arg>
	"""

	def run(self, params, args):
		self.beginOutput()

		for host in self.getHostnames(args):
			rows = self.db.select("""
				id, public_key from public_keys
				where node = (select id from nodes where name = %s)
				""", (host,)
			)

			for key_id, key in rows:
				for line in key.split('\n'):
					self.addOutput(host, (key_id, line))

		self.endOutput(header=['host', 'id', 'public key'], trimOwner=False)
