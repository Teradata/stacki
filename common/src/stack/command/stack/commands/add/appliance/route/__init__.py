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
from stack.exception import ParamRequired, CommandError


class Command(stack.commands.add.appliance.command):
	"""
	Add a route for an appliance type in the cluster

	<arg type='string' name='appliance'>
	The appliance type (e.g., 'backend').
	</arg>
	
	<param type='string' name='address' optional='0'>
	Host or network address
	</param>
	
	<param type='string' name='gateway' optional='0'>
	Network or device gateway
	</param>

	<param type='string' name='netmask'>
	Specifies the netmask for a network route.  For a host route
	this is not required and assumed to be 255.255.255.255
	</param>
	"""

	def run(self, params, args):

		apps = self.getApplianceNames(args)

		(address, gateway, netmask, interface) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255'),
			('interface', None),
			])
		
		if len(args) == 0:
			raise ParamRequired(self, 'appliance')

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
		# for any of the given appliances raise a CommandError.
		for app in apps:
			rows = self.db.select("""* from
				appliance_routes r, appliances a where
				r.appliance=a.id and r.network=%s
				and a.name=%s""",
				(address, app))
			if rows:
				raise CommandError(self, 'route exists')

		#
		# if interface is being set, check if it exists first
		#
		if not interface:
			interface = None

		# Now that we know things will work insert the route for
		# all the appliances
		for app in apps:
			self.db.execute("""insert into appliance_routes values 
				((select id from appliances where name=%s),
				%s, %s, %s, %s, %s)""" ,
				(app, address, netmask, gateway, subnet, interface))
