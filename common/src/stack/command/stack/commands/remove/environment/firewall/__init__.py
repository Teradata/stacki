# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.remove.environment.command):
	"""
	Remove a firewall service rule for an environment.
	To remove the rule, you must supply the name of the rule.

	<arg type='string' name='environment' repeat='1'>
	An environment name.
	</arg>

	<param type='string' name='rulename' optional='0'>
	Name of the environment-specific rule
	</param>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		self.command('remove.firewall', self._argv + ['scope=environment'], verbose_errors = False)
		return self.rc
