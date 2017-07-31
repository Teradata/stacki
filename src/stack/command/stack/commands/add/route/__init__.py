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

import stack.commands
from stack.exception import *

class Command(stack.commands.add.command):
	"""
	Add a route for all hosts in the cluster
	
	<param type='string' name='address' optional='0'>
	Host or network address
	</param>
	
	<param type='string' name='gateway' optional='0'>
	Network (e.g., IP address), subnet name (e.g., 'private', 'public'), or
	a device gateway (e.g., 'eth0).
	</param>

	<param type='string' name='netmask'>
	Specifies the netmask for a network route.  For a host route
	this is not required and assumed to be 255.255.255.255
	</param>
	"""

	def run(self, params, args):

		(address, gateway, netmask) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255')
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
		
		rows = self.db.execute("""select * from global_routes
			where network='%s'""" % address)
		if rows:
			raise CommandError(self, 'route exists')
			
		self.db.execute("""insert into global_routes
				values ('%s', '%s', %s, %s)""" %
				(address, netmask, gateway, subnet))

