# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.exception import CommandError


class Command(stack.commands.list.appliance.command):

	"""
	Lists the XML profile for a given appliance type. This is useful
	for high level debugging but will be missing any host specific
	variables. It cannot be used to pass into 'rocks list host profile'
	to create a complete Kickstart/Jumpstart profile.
	
	<arg optional='1' type='string' name='appliance' repeat='1'>
	Optional list of appliance names.
	</arg>
		
	<example cmd='list appliance xml compute'>
	Lists the XML profile for a compute appliance.
	</example>

	<example cmd='list appliance xml'>
	Lists the XML profile for all appliance types.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		for app in self.getApplianceNames(args):
			self.db.execute("""select name from appliances
				where name='%s'""" % app)
			try:
				(name, ) = self.db.fetchone()
			except TypeError:
				raise CommandError(self, 'no such appliance "%s"' % app)
			if name:
				xml = self.command('list.node.xml', [name])
				for line in xml.split('\n'):
					self.addOutput(app, line)
		self.endOutput(padChar='')

