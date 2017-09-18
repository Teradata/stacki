# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.remove.host.command):
	"""
	Remove a static route for a host.

	<arg type='string' name='host' repeat='1'>
	Name of a host machine.
	</arg>

	<param type='string' name='address' optional='0'>
	The address of the static route to remove. This argument is required.
	</param>

	<example cmd='remove host route backend-0-0 address=1.2.3.4'>
	Remove the static route for the host 'backend-0-0' that has the
	network address '1.2.3.4'.
	</example>
	"""

	def run(self, params, args):
		
		(address, ) = self.fillParams([ ('address', None, True) ])

		for host in self.getHostnames(args):
			self.db.execute("""
			delete from node_routes where 
			node = (select id from nodes where name='%s')
			and network = '%s'
			""" % (host, address))

