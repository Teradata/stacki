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


class command(stack.commands.remove.command):
	def deleteRule(self, table, rulename, extrasql=None):

		assert table
		assert rulename

		query = 'select * from %s where name="%s"' % (table, rulename)
		if extrasql:
			query = "%s and %s" % (query, extrasql)
		rows = self.db.execute(query)

		if rows == 0:
			raise CommandError(self, 'Could not find rule %s in %s' % (rulename, table))

		query = 'delete from %s where name="%s"' % (table, rulename)
		if extrasql:
			query = "%s and %s" % (query, extrasql)
		self.db.execute(query)


class Command(command):
	"""
	Remove a global firewall rule. To remove a rule, you must supply
	the name of the rule.
	
	<param type='string' name='rulename' optional='0'>
	Name of the rule
	</param>
	"""

	def run(self, params, args):
		
		(rulename, ) = self.fillParams([ ('rulename', None, True) ])
		
		self.deleteRule('global_firewall', rulename)

