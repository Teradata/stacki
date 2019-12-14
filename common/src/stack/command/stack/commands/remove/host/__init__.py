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
from stack.exception import ArgRequired, CommandError


class command(stack.commands.HostArgumentProcessor,
		stack.commands.remove.command):
	pass


class Command(command):
	"""
	Remove a host from the database. This command will remove all
	related database rows for each specified host.

	<arg type='string' name='host' repeat='1'>
	List of hosts to remove from the database.
	</arg>

	<example cmd='remove host backend-0-0'>
	Remove the backend-0-0 from the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)
		if not hosts:
			raise ArgRequired(self, 'host')

		# Don't allow the user to remove the host the command
		# is running on.  Right now that means cannot remove
		# the Frontend, but checked this way will allow for
		# future multiple Frontend's where you may still want
		# to remove some but not all of them.
		me = self.db.getHostname()
		if me in hosts:
			raise CommandError(self, 'cannot remove "%s"' % me)

		self.runPlugins(hosts)
		self.command('sync.config')
