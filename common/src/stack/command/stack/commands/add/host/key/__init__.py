# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.add.host.command):
	"""
	Add a public key for a host. One use of this public key is to 
	authenticate messages sent from remote services.

	<arg type='string' name='host' optional='0'>
	Host name of machine
	</arg>
	
	<param type='string' name='key'>
	A public key. This can be the actual key or it can be a path name to
	a file that contains a public key (e.g., /tmp/public.key).
	</param>
	"""

	def run(self, params, args):
		host = self._get_single_host(args)

		key, = self.fillParams([ ('key', None, True) ])

		# See if the key is a file name
		if os.path.exists(key):
			with open(key, 'r') as f:
				key = f.read()

		# Check if the key already exists
		if self.db.select("""count(ID) from public_keys where
			node = (select id from nodes where name = %s) and
			public_key = %s """, (host, key)
		)[0][0] != 0:
			raise CommandError(self, f'the public key already exists for host {host}')

		# Add the key
		self.db.execute("""insert into public_keys(node, public_key)
			values ((select id from nodes where name = %s), %s)""",
			(host, key)
		)
