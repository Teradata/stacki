# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import os
import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.add.host.command):
	"""
	Add a public key for a host. One use of this public key is to 
	authenticate messages sent from remote services.

	<arg type='string' name='host'>
	Host name of machine
	</arg>
	
	<param type='string' name='key'>
	A public key. This can be the actual key or it can be a path name to
	a file that contains a public key (e.g., /tmp/public.key).
	</param>
	"""

	def run(self, params, args):
		key, = self.fillParams([ ('key', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'host')
		hosts = self.getHostnames(args)
		if len(hosts) > 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]

		#
		# see if the key is a file name
		#
		if os.path.exists(key):
			file = open(key, 'r')
			public_key = file.read()
			file.close()
		else:
			public_key = key

		#
		# check if the key already exists
		#
		rows = self.db.execute("""select * from public_keys where
			node = (select id from nodes where name = '%s') and
			public_key = '%s' """ % (host, public_key))

		if rows == 1:
			raise CommandError(self, 'the public key already exists for host %s'
				% host)

		#
		# add the key
		#
		self.db.execute("""insert into public_keys (node, public_key)
			values ((select id from nodes where name = '%s'),
			'%s') """ % (host, public_key))

