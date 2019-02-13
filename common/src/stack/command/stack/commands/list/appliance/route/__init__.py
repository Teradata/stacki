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


class Command(stack.commands.list.appliance.command):
	"""
	List the routes for a given appliance type.

	<arg optional='1' type='string' name='appliance' repeat='1'>
	Zero, one or more appliance names. If no appliance names are supplied,
	the routes for all the appliances are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.route', self._argv + ['scope=appliance']))
		return self.rc
