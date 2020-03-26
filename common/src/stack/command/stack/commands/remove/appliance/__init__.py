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
from stack.commands import ApplianceArgProcessor
from stack.exception import ArgRequired, CommandError

class command(ApplianceArgProcessor, stack.commands.remove.command):
	pass

class Command(command):
	"""
	Remove an appliance definition from the system. This can be
	called with just the appliance or it can be further
	qualified by supplying the root XML node name and/or the
	graph XML file name.

	<arg type='string' name='name'>
	The name of the appliance.
	</arg>
	
	<example cmd='remove appliance backend'>
	Removes the backend appliance from the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'appliance')

		appliances = self.getApplianceNames(args)

		#
		# don't remove the default appliance
		#
		if 'backend' in appliances:
			raise CommandError(self, 'cannot remove default appliance')

		#
		# check if the appliance is associated with any hosts
		#
		for appliance in appliances:
			for row in self.call('list.host'):
				if row['appliance'] == appliance:
					raise CommandError(self, 'cannot remove appliance "%s" because host "%s" is assigned to it' % (appliance, row['host']))

		#
		# good to go
		#
		for appliance in appliances:
			self.db.execute('delete from appliances where name=%s', (appliance,))
