# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.list.appliance.command):
	"""
	List the storage partition configuration for a given appliance(s).

	<arg optional='1' type='string' name='appliance' repeat='1'>
	Zero, one or more appliance names. If no appliance names are supplied,
	the routes for all the appliances are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.storage.partition', self._argv + ['scope=appliance']))
		return self.rc
