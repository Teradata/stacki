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
from stack.exception import ArgRequired


class Command(stack.commands.remove.appliance.command):
	"""
	Remove a static route for an appliance type.

	<arg type='string' name='appliance' optional='0' repeat='1'>
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
		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		self.command('remove.route', self._argv + ['scope=appliance'], verbose_errors = False)
		return self.rc
