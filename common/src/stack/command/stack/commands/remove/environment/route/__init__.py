# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.environment.command):
	"""
	Remove an environment static route.

	<arg type='string' name='environment' optional='0'>
	Environment name
	</arg>

	<param type='string' name='address' optional='0'>
	The address of the route to remove.
	</param>
	"""


	def run(self, params, args):

		(address, ) = self.fillParams([('address', None, True)])

		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		for environment in self.getEnvironmentNames(args):
			env = self.db.select("""id FROM environments WHERE name=%s""", environment)[0][0]

			self.db.execute("""DELETE FROM environment_routes WHERE
					environment=%s AND network=%s""", (env, address))

