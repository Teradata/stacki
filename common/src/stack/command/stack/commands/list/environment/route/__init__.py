# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands


class Command(stack.commands.list.environment.command):
	"""
	List the routes for one or more environments

	<arg optional='1' type='string' name='environment' repeat='1'>
	Zero, one or more environments.
	</arg>

	"""

	def run(self, params, args):

		self.beginOutput()

		for environment in self.getEnvironmentNames(args):
			env_id = self.db.select("""id FROM environments WHERE name = %s""", environment)[0][0]

			rows = self.db.select("""network, netmask, gateway, subnet, interface
					FROM environment_routes WHERE environment = %s""", [env_id])

			for (network, netmask, gateway, subnet, interface) in rows:
				if subnet:
					rows = self.db.select("""name FROM subnets WHERE id = %s""", [subnet])
					if rows:
						subnet = rows[0][0]
						gateway = None

				self.addOutput(environment, (network, netmask, gateway, subnet, interface))

		self.endOutput(header=['environment', 'network', 'netmask', 'gateway',
				       'subnet', 'interface'], trimOwner=0)

