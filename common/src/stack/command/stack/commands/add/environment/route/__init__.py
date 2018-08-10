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

		#
		# determine if this is a subnet identifier
		#
		subnet = 0
		rows = self.db.execute("""select id from subnets where
			name = %s """, gateway)

		if rows == 1:
			subnet, = self.db.fetchone()
			gateway = "''"  # NULL?
		else:
			subnet = None

		# Verify the route doesn't already exist. If it does
		# for any of the environments, raise a CommandError.

		for environment in environments:
			rows = self.db.execute("""select * from
				environment_routes where
				network=%s and environment=%s""",
				(address, environment))
			if rows:
				raise CommandError(self, 'route exists')

		#
		# if interface is being set, check if it exists first
		#
		if interface:
			rows = self.db.execute("""select * from networks
				where node=1 and device=%s""", interface)
			if not rows:
				raise CommandError(self, 'interface does not exist')
		else:
			interface='NULL'

		# Now that we know things will work insert the route for
		# all the environments

		((env, ), ) = self.db.select("""id FROM environments WHERE name=%s""", environment)

		for environment in environments:
			self.db.execute("""insert into environment_routes values
				(%s, %s, %s, %s, %s, %s)""",
				(env, address, netmask, gateway, subnet, interface))

