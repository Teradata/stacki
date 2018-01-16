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

import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.remove.host.command):
	"""
	Remove a public key for a host.
	
	<arg optional='0' type='string' name='host'>
	A host name.
	</arg>

	<param type='string' name='id'>
	The ID of the key you wish to remove. To get the key id, execute:
	"rocks list host key"
	</param>
	"""

	def run(self, params, args):
		id, = self.fillParams([ ('id', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'host')
		hosts = self.getHostnames(args)
		if len(hosts) > 1:
			raise ArgUnique(self, 'host')

		host = hosts[0]

		rows = self.db.execute("""select * from public_keys where
			id = %s and node = (select id from
			nodes where name = '%s') """ % (id, host))

		if rows == 0:
			msg = "public key with id %s " % id
			msg += "doesn't exist for host %s" % host
			raise CommandError(self, msg)
		
		self.db.execute("""delete from public_keys where
			id = %s and node = (select id from
			nodes where name = '%s') """ % (id, host))

