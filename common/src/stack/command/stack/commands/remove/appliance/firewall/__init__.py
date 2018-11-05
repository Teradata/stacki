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
	Remove a firewall service rule for an appliance type.
	To remove the rule, you must supply the name of the rule.

	<arg type='string' name='appliance' repeat='1'>
	Name of an appliance type (e.g., "backend").
	</arg>

	<param type='string' name='rulename' optional='0'>
	Name of the Appliance-specific rule
	</param>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		self.command('remove.firewall', self._argv + ['scope=appliance'])
		return self.rc
