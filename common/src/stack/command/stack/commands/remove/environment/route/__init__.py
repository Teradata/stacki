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

