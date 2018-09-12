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

	<example cmd='list appliance xml backend'>
	Lists the XML profile for a backend appliance.
	</example>

	<example cmd='list appliance xml'>
	Lists the XML profile for all appliance types.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		for app in self.getApplianceNames(args):
			# Get the appliance attributes
			attrs = {
				row['attr']: row['value']
				for row in self.call('list.appliance.attr', [app])
			}
			kickstartable = attrs.get('kickstartable', 'False')

			# Only generate XML for appliances with a node attribute
			# and kickstartable set to True
			if 'node' in attrs and self.str2bool(kickstartable):
				xml = self.command('list.node.xml', [attrs['node']])
				for line in xml.split('\n'):
					self.addOutput(app, line)

		self.endOutput(padChar='')
