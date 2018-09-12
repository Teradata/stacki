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
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.remove.host.command):
	"""
	Remove a firewall rule for a host. To remove a rule,
	you must supply the name of the rule.

	<arg type='string' name='host' repeat='1'>
	Name of a host machine.
	</arg>

	<param type='string' name='rulename' optional='0'>
	Name of host-specific rule
	</param>

	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		(rulename, ) = self.fillParams([ ('rulename', None, True) ])

		for host in self.getHostnames(args):
			# Make sure our rule exists
			if self.db.count("""
				(*) from node_firewall
				where name=%s and node=(
					select id from nodes where name=%s
				)""", (rulename, host)
			) == 0:
				raise CommandError(
					self,
					f'firewall rule {rulename} does not '
					f'exist for host {host}'
				)

			# It exists, so delete it
			self.db.execute("""
				delete from node_firewall
				where name=%s and node=(
					select id from nodes where name=%s
				)
			""", (rulename, host))
