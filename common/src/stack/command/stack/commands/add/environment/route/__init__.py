# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
<<<<<<< HEAD
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
=======
>>>>>>> b7ec72a9ba58d8a56cc98e6d1713e95dba37f7ba


import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.add.environment.command):
	"""
	Add a route for an environment

	<arg type='string' name='environment' optional='0'>
	Environment name
	</arg>

	<param type='string' name='address' optional='0'>
	Host or network address
	</param>

	<param type='string' name='netmask' optional='0'>
	Specifies the netmask for a network route (default 255.255.255.255).
	</param>

	<param type='string' name='gateway'>
	Network or device gateway
	</param>

	<param type='string' name='interface'>
	Specific interface to send traffic through. Should only be used if
	you need traffic to through a VLAN interface (e.g., 'eth0.1').
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
			raise ArgRequired(self, 'environment')

		environments = self.getEnvironmentNames(args)
		env_ids = []

		for environment in self.getEnvironmentNames(args):
			env_ids.append(self.db.select("""id FROM environments
						WHERE name = %s""", environment)[0][0])

		#
		# determine if this is a subnet identifier
		#
		rows = self.db.select("""id FROM subnets WHERE name = %s""", gateway)

		if rows:
			subnet = rows[0][0]
			gateway = ''
		else:
			subnet = None

		# Verify the route doesn't already exist. If it does
		# for any of the environments, raise a CommandError.

		for env_id in env_ids:
			rows = self.db.select("""* FROM environment_routes
				WHERE network = %s AND environment = %s""",
				(address, env_id))
			if rows:
				raise CommandError(self, 'route exists')

		#
		# if interface is being set, check if it exists first
		#
		if interface:
			rows = self.db.select("""* FROM networks
				WHERE node = 1 AND device = %s""", interface)
			if not rows:
				raise CommandError(self, 'interface does not exist')

		# Now that we know things will work insert the route for
		# all the environments

		for env_id in env_ids:
			self.db.execute("""INSERT INTO environment_routes VALUES
				(%s, %s, %s, %s, %s, %s)""",
				(env_id, address, netmask, gateway, subnet, interface))

