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

class command(ApplianceArgProcessor, stack.commands.list.command):
	pass


class Command(command):
	"""
	Lists the appliances defined in the cluster database.

	<arg optional='1' type='string' name='appliance' repeat='1'>
	Optional list of appliance names.
	</arg>

	<example cmd='list appliance'>
	List all known appliances.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		for app in self.getApplianceNames(args):
			rows = self.db.select(
				'public from appliances where name=%s',
				(app,)
			)
			self.addOutput(app, rows[0])

		self.endOutput(header=['appliance', 'public'])
