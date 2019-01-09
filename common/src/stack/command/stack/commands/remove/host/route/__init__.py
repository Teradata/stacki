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

	<arg type='string' name='host' repeat='1' optional='0'>
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
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		self.command('remove.route', self._argv + ['scope=host'])
		return self.rc
