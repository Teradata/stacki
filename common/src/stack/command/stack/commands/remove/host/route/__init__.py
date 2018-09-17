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
from stack.exception import ArgRequired


class Command(stack.commands.remove.host.command):
	"""
	Remove a static route for a host.

	<arg type='string' name='host' repeat='1'>
	Name of a host machine.
	</arg>

	<param type='string' name='address' optional='0'>
	The address of the static route to remove. This argument is required.
	</param>

	<param type='string' name='syncnow' optional='1'>
	If set to true, the routing table will be updated as well as the db.
	</param>

	<example cmd='remove host route backend-0-0 address=1.2.3.4'>
	Remove the static route for the host 'backend-0-0' that has the
	network address '1.2.3.4'.
	</example>

	<example cmd='remove host route backend-0-0 address=1.2.3.4 syncnow=true'>
	Remove the static route for the host 'backend-0-0' that has the
	network address '1.2.3.4' and remove the route from the routing table.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)
		if not hosts:
			raise ArgRequired(self, 'host')

		(address, syncnow, ) = self.fillParams([
			('address', None, True),
			('syncnow', None)
		])

		syncnow = self.str2bool(syncnow)
		me = self.db.getHostname()

		for host in hosts:
			result = self.db.execute("""
				delete from node_routes
				where node=(select id from nodes where name=%s) and network=%s
			""", (host, address))

			# Remove the route from the frontend, if needed
			if syncnow and result and host == me:
				self._exec(f'route del -host {address}', shlexsplit=True)
