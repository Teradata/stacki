# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


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

		(rulename, ) = self.fillParams([ ('rulename', None, True) ])

		for environment in self.getEnvironmentNames(args):
			# Make sure our rule exists
			if self.db.count("""
				(*) from environment_firewall
				where name=%s and environment=(
					select id from environments where name=%s
				)""", (rulename, environment)
			) == 0:
				raise CommandError(
					self,
					f'firewall rule {rulename} does not '
					f'exist for environment {environment}'
				)

			# It exists, so delete it
			self.db.execute("""
				delete from environment_firewall
				where name=%s and environment=(
					select id from environments where name=%s
				)
			""", (rulename, environment))
