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

class Command(stack.commands.remove.appliance.command):
	"""
	Remove a static route for an appliance type.

	<arg type='string' name='appliance'>
	Appliance name. This argument is required.
	</arg>

	<param type='string' name='address' optional='0'>
	The address of the static route to remove.
	</param>

	<example cmd='remove appliance route compute address=1.2.3.4'>
	Remove the static route for the 'compute' appliance that has the
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

