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
from stack.argument_processors.appliance import ApplianceArgProcessor

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
		
		info = {} # greedy select for caching
		for name, sux, managed in self.db.select("""
			name, sux, if(managed, 'True', 'False') 
			from appliances"""):
			info[name] = (sux, managed)

		self.beginOutput()
		for app in self.getApplianceNames(args):
			self.addOutput(app, info[app])

		self.endOutput(header=['appliance', 'sux', 'managed'])
