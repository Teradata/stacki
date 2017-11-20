# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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
from stack.exception import CommandError


class Command(stack.commands.add.host.command):
	"""
	Add a route for a host

	<arg type='string' name='host' repeat='1'>
	Host name of machine
	</arg>
	
	<param type='string' name='address'>
	Host or network address
	</param>
	
	<param type='string' name='gateway'>
	Network or device gateway
	</param>

	<param type='string' name='netmask'>
	Specifies the netmask for a network route.  For a host route
	this is not required and assumed to be 255.255.255.255
	</param>
	"""

	def run(self, params, args):

		hosts = self.getHostnames(args)
		
		(address, gateway, netmask, interface) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255'),
			('interface', None),
			])
		
		#
		# determine if this is a subnet identifier
		#
		subnet = 0
		rows = self.db.execute("""select id from subnets where
			name = '%s' """ % gateway)

		if rows == 1:
			subnet, = self.db.fetchone()
			gateway = "''"
		else:
			subnet = 'NULL'
			gateway = "'%s'" % gateway
		
		# Verify the route doesn't already exist.  If it does
		# for any of the hosts raise a CommandError.
		
		for host in hosts:
			rows = self.db.execute("""select * from 
				node_routes r, nodes n where
				r.node=n.id and r.network='%s' 
				and n.name='%s'""" %	
				(address, host)) 
			if rows:
				raise CommandError(self, 'route exists')

		#
		# if interface is being set, check if it exists first
		#
		if interface:
			rows = self.db.execute("""select * from networks
				where node=1 and device='%s'""" % interface)
			if not rows:
				raise CommandError(self, 'interface does not exist')
		else:
			interface='NULL'
		
		# Now that we know things will work insert the route for
		# all the hosts
		
		for host in hosts:	
			self.db.execute("""insert into node_routes values 
				((select id from nodes where name='%s'),
				'%s', '%s', %s, %s, '%s')""" %
				(host, address, netmask, gateway, subnet, interface))

