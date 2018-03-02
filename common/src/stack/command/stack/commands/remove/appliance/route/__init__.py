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
from stack.exception import ArgRequired


class Command(stack.commands.remove.appliance.command):
	"""
	Remove a static route for an appliance type.

	<arg type='string' name='appliance'>
	Appliance name. This argument is required.
	</arg>

	<param type='string' name='address' optional='0'>
	The address of the static route to remove.
	</param>

	<example cmd='remove appliance route backend address=1.2.3.4'>
	Remove the static route for the 'backend' appliance that has the
	network address '1.2.3.4'.
	</example>
	"""

	def run(self, params, args):
		
		(address, ) = self.fillParams([ ('address', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		for appliance in self.getApplianceNames(args):
			self.db.execute("""
			delete from appliance_routes where 
			appliance = (select id from appliances where name='%s')
			and network = '%s'
			""" % (appliance, address))

