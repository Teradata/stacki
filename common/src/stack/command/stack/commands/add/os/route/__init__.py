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
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.add.os.command):
	"""
	Add a route for an OS type

	<arg type='string' name='os'>
	The OS type (e.g., 'linux', 'sunos', etc.). This argument is required.
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

		(address, gateway, netmask, interface) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255'),
			('interface', None)
			])
		
		if len(args) == 0:
			raise ArgRequired(self, 'os')

		oses = self.getOSNames(args)

		# check if the user has put a subnet name in the gateway field
		subnet = self.db.select("""id from subnets where name=%s """, [gateway])
		if subnet:
			# if they have, set the gateway to '' and pull the subnet name
			# out of the returned tuple
			gateway = ''
			subnet = subnet[0][0]
		else:
			# if they haven't, set the subnet to None and leave the user
			# specified gateway in the gateway field
			subnet = None
		
		# Verify the route doesn't already exist.  If it does
		# for any of the given OSes raise a CommandError.
		
		for os in oses:
			rows = self.db.select("""* from
				os_routes where 
				network=%s and os=%s""" ,
				(address, os))
			if rows:
				raise CommandError(self, 'route exists')
		#
		# if interface is being set, check if it exists first
		#
		if interface:
			rows = self.db.select("""* from networks
				where node=1 and device=%s""", interface)
			if not rows:
				raise CommandError(self, 'interface does not exist')
		else:
			interface= None
		
		# Now that we know things will work insert the route for
		# all the OSes
		
		for os in oses:	
			self.db.execute("""insert into os_routes values 
				(%s, %s, %s, %s, %s, %s)""" ,
				(os, address, netmask, gateway, subnet, interface))
