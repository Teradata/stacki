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
import subprocess


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
	if set to true, the routing table will be updated as well as the db.
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
		
		(address, syncnow, ) = self.fillParams([ 
			('address', None, True),
			('syncnow', None)
			])

		syncnow = self.str2bool(syncnow)

		for host in self.getHostnames(args):
			res = self.db.execute("""
			delete from node_routes where 
			node = (select id from nodes where name='%s')
			and network = '%s'
			""" % (host, address))

			if res and host in self.getHostnames(['localhost']):
				if syncnow:
					del_route = ['route', 'del', '-host', address]

					# remove route from routing table
					p = subprocess.Popen(del_route, stdout=subprocess.PIPE)
