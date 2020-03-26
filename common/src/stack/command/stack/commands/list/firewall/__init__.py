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

class Command(ScopeArgProcessor, stack.commands.list.command):
	"""
	Lists the set of global firewalls.

	<example cmd='list firewall'>
	List the global firewall rules.
	</example>
	"""

	def _sorter(self, table, action):
		table_scores = {'filter': 10, 'nat': 20, 'raw': 30, 'mangle': 40}
		action_scores = {'ACCEPT': 1, 'DROP': 3, 'REJECT': 4}

		# Sum the scores from the tables, with unknown table types
		# getting 0 (when shouldn't happen, since it is an enum) and
		# other actions getting 2.
		return table_scores.get(table, 0) + action_scores.get(action, 2)

	def _host_scope_sorter(self, rule):
		return self._sorter(rule[1], rule[5])

	def _other_scope_sorter(self, rule):
		return self._sorter(rule[2], rule[6])

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		self.beginOutput()
		for scope_mapping in scope_mappings:
			if scope == 'host':
				# Host scope gets intrinsic rules first
				self.runPlugins(scope_mapping.node_id)

				# Get the host's info for the scope linking
				host, appliance_id, os_id, environment_id = self.db.select("""
					nodes.name, appliance, boxes.os, environment
					FROM nodes, boxes
					WHERE nodes.id = %s AND nodes.box = boxes.id
				""", (scope_mapping.node_id,))[0]

				# Get all the rules for all scopes that match the host's info
				rules = self.db.select("""
					firewall_rules.name, table_type, service, protocol, chain,
					action, in_subnet.name, out_subnet.name, flags, comment,
					UPPER(LEFT(scope_map.scope, 1)), 'var'
					FROM firewall_rules
					LEFT JOIN subnets in_subnet
						ON firewall_rules.in_subnet_id = in_subnet.id
					LEFT JOIN subnets out_subnet
						ON firewall_rules.out_subnet_id = out_subnet.id
					INNER JOIN scope_map
						ON firewall_rules.scope_map_id = scope_map.id
					WHERE scope_map.scope = 'global'
					OR (scope_map.scope = 'appliance' AND scope_map.appliance_id <=> %s)
					OR (scope_map.scope = 'os' AND scope_map.os_id <=> %s)
					OR (scope_map.scope = 'environment' AND scope_map.environment_id <=> %s)
					OR (scope_map.scope = 'host' AND scope_map.node_id <=> %s)
					ORDER BY scope_map.scope DESC, firewall_rules.id ASC
				""", (appliance_id, os_id, environment_id, scope_mapping.node_id))

				# The rules come out of the DB with the higher value scopes
				# first. Surprisingly, there is no simple way in SQL to squash
				# these rules down by scope value. So, we do it here instead.
				seen_names = set()
				squashed_rules = []
				for rule in rules:
					if rule[0] not in seen_names:
						squashed_rules.append(rule)
						seen_names.add(rule[0])

				# Now we output our squashed rules, sorting them on the fly
				for rule in sorted(squashed_rules, key=self._host_scope_sorter):
					self.addOutput(host, rule)

			else:
				# All the other scopes just list their rules
				rules = self.db.select("""
					COALESCE(appliances.name, oses.name, environments.name, ''),
					firewall_rules.name, table_type, service, protocol, chain,
					action, in_subnet.name, out_subnet.name, flags, comment,
					UPPER(LEFT(scope_map.scope, 1)), 'var'
					FROM firewall_rules
					LEFT JOIN subnets in_subnet
						ON firewall_rules.in_subnet_id = in_subnet.id
					LEFT JOIN subnets out_subnet
						ON firewall_rules.out_subnet_id = out_subnet.id
					INNER JOIN scope_map
						ON firewall_rules.scope_map_id = scope_map.id
					LEFT JOIN appliances
						ON scope_map.appliance_id = appliances.id
					LEFT JOIN oses
						ON scope_map.os_id = oses.id
					LEFT JOIN environments
						ON scope_map.environment_id = environments.id
					WHERE scope_map.scope = %s
					AND scope_map.appliance_id <=> %s
					AND scope_map.os_id <=> %s
					AND scope_map.environment_id <=> %s
					AND scope_map.node_id <=> %s
					ORDER BY firewall_rules.id ASC
				""", scope_mapping)

				for rule in sorted(rules, key=self._other_scope_sorter):
					self.addOutput(rule[0], rule[1:])

		if scope == 'global':
			header = ''
		else:
			header = scope

		self.endOutput(header=[
			header, 'name', 'table', 'service','protocol', 'chain', 'action',
			'network', 'output-network', 'flags', 'comment', 'source', 'type'
		])
