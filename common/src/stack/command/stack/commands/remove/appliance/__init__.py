# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
from stack.exception import ArgRequired, ArgNotFound


class command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.remove.command):
	pass


class Command(command):
	"""
	Remove an appliance definition from the system.

	<arg type='string' name='appliance' optional='0' repeat='1'>
	One or more appliances
	</arg>

	<example cmd='remove appliance hadoop'>
	Removes the hadoop appliance from the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'appliance')

		# Make sure the appliances are valid
		self.appliances_exist(args)

		# Remove the appliances
		self.graphql_mutation("remove_appliance(names: %s)", (args,))
