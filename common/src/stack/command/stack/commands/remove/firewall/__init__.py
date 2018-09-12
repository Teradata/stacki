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


class Command(stack.commands.remove.command):
	"""
	Remove a global firewall rule. To remove a rule, you must supply
	the name of the rule.

	<param type='string' name='rulename' optional='0'>
	Name of the rule
	</param>
	"""

	def run(self, params, args):
		(rulename, ) = self.fillParams([ ('rulename', None, True) ])

		# Make sure our rule exists
		if self.db.count(
			'(*) from global_firewall where name=%s',
			(rulename,)
		) == 0:
			raise CommandError(self, f'firewall rule {rulename} does not exist')

		# It exists, so delete it
		self.db.execute(
			'delete from global_firewall where name=%s',
			(rulename,)
		)
