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
from stack.commands import ScopeArgProcessor
from stack.exception import CommandError

class Command(ScopeArgProcessor, stack.commands.remove.command):
	"""
	Remove a global firewall rule. To remove a rule, you must supply
	the name of the rule.

	<param type='string' name='rulename' optional='0'>
	Name of the rule
	</param>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		(name, ) = self.fillParams([('rulename', None, True)])

		scope_ids = []
		for scope_mapping in scope_mappings:
			# Check that the rule name exists for the scope
			rows = self.db.select("""
		 		scope_map.id FROM firewall_rules,scope_map
				WHERE firewall_rules.scope_map_id = scope_map.id
				AND firewall_rules.name = %s
				AND scope_map.scope = %s
				AND scope_map.appliance_id <=> %s
				AND scope_map.os_id <=> %s
				AND scope_map.environment_id <=> %s
				AND scope_map.node_id <=> %s
			""", (name, *scope_mapping))

			if not rows:
		 		raise CommandError(self, f'rule named "{name}" does not exist')

			scope_ids.append(rows[0][0])

		# Rules existed for all the scope mappings, so delete them
		# Note: We just delete the scope mapping, the ON DELETE CASCADE takes
		# care of removing the firewall_rules table entry for us.
		self.db.execute('delete from scope_map where id in %s', (scope_ids,))
