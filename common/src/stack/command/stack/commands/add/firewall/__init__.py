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

import re
import string
import uuid

import stack.commands
from stack.commands import ScopeArgProcessor
from stack.exception import CommandError, ParamRequired, ParamError
from stack.util import blank_str_to_None


class Command(ScopeArgProcessor, stack.commands.add.command):
	"""
	Add a global firewall rule for the all hosts in the cluster.

	<param type='string' name='service' optional='0'>
	A comma seperated list of service identifier, port number or port range.

	For example "www", 8080, 0:1024, or "1:1024,8080".

	To have this firewall rule apply to all services, specify the keyword 'all'.
	</param>

	<param type='string' name='protocol' optional='0'>
	The protocol associated with the rule. For example, "tcp" or "udp".

	To have this firewall rule apply to all protocols, specify the
	keyword 'all'.
	</param>

	<param type='string' name='network'>
	The network this rule should be applied to. This is a named network
	(e.g., 'private') and must be one listed by the command
	'stack list network'.

	By default, the rule will apply to all networks.
	</param>

	<param type='string' name='output-network' optional='1'>
	The output network this rule should be applied to. This is a named
	network (e.g., 'private') and must be one listed by the command
	'stack list network'.

	By default, the rule will apply to all networks.
	</param>

	<param type='string' name='chain' optional='0'>
	The iptables 'chain' this rule should be applied to (e.g.,
	INPUT, OUTPUT, FORWARD).
	</param>

	<param type='string' name='action' optional='0'>
	The iptables 'action' this rule should be applied to (e.g.,
	ACCEPT, REJECT, DROP).
	</param>

	<param type='string' name='flags'>
	Optional flags associated with this rule. An example flag is:
	"-m state --state RELATED,ESTABLISHED".
	</param>

	<param type='string' name='comment'>
	A comment associated with this rule. The comment will be printed
	directly above the rule in the firewall configuration file.
	</param>

	<param type='string' name='table'>
	The table to add the rule to. Valid values are 'filter',
	'nat', 'mangle', and 'raw'. If this parameter is not
	specified, it defaults to 'filter'
	</param>

	<param type='string' name='rulename'>
	The rule name for the rule to add. This is the handle by
	which the admin can remove or override the rule.
	</param>

	<example cmd='add firewall network=public service="ssh"
	protocol="tcp" action="ACCEPT" chain="INPUT" flags="-m state --state NEW"
	table="filter" rulename="accept_public_ssh"'>
	Accept TCP packets for the ssh service on the public network on
	the INPUT chain in the "filter" table and apply the "-m state --state NEW"
	flags to the rule.
	If 'eth1' is associated with the public network, this will be
	translated as the following iptables rule:
	"-A INPUT -i eth1 -p tcp --dport ssh -m state --state NEW -j ACCEPT"
	</example>

	<example cmd='add firewall network=private service="all" protocol="all"
	action="ACCEPT" chain="INPUT"'>
	Accept all protocols and all services on the private network on the
	INPUT chain.
	If 'eth0' is the private network, then this will be translated as
	the following iptables rule:
	"-A INPUT -i eth0 -j ACCEPT"
	</example>
	"""

	def run(self, params, args):
		# Get the scope and make sure the args are valid
		scope, = self.fillParams([('scope', 'global')])
		scope_mappings = self.getScopeMappings(args, scope)

		# Now validate the params
		(name, table_type, chain, action, service, protocol, input_network,
		output_network, flags, comment) = self.fillParams([
			('rulename', None),
			('table', 'filter'),
			('chain', None, True),
			('action', None, True),
			('service', None, True),
			('protocol', None, True),
			('network', None),
			('output-network', None),
			('flags', None),
			('comment', None)
		])

		# Generate a random firewall rule name if needed
		if not name:
			name = str(uuid.uuid1())

		# Make sure table is a valid choice
		if table_type not in {'filter', 'raw', 'mangle', 'nat'}:
			raise ParamError(self, 'table', 'is not valid')

		# Catch any blank parameters in chain, action, service, and protocol
		if not chain:
			raise ParamRequired(self, 'chain')

		if not action:
			raise ParamRequired(self, 'action')

		if not service:
			raise ParamRequired(self, 'service')

		if not protocol:
			raise ParamRequired(self, 'protocol')

		# Uppercase chain and action
		chain = chain.upper()
		action = action.upper()

		# Convert our networks to subnet ids
		input_network = blank_str_to_None(input_network)
		if input_network:
			rows = self.db.select('id from subnets where name=%s', (input_network,))

			if not rows:
				raise CommandError(
					self, f'"{input_network}" is not a valid network'
				)

			in_subnet_id = rows[0][0]
		else:
			in_subnet_id = None

		output_network = blank_str_to_None(output_network)
		if output_network:
			rows = self.db.select('id from subnets where name = %s', (output_network,))

			if not rows:
				raise CommandError(
					self, f'"{output_network}" is not a valid network'
				)

			out_subnet_id = rows[0][0]
		else:
			out_subnet_id = None

		# Normalize the service sting by stripping whitespace and lowercasing it
		service = re.sub(r'\s+', '', service).lower()

		# Make sure the service string is valid
		if not re.fullmatch(r"""
			all 				# 'all'
			|				# OR
			(?:
				\d+(?::\d+)?		# a port number with optional ':N' range
				|			# OR
				[a-z]+			# a service name
			)
			(?:
				,			# zero or more comma-seperated repetitions
				(?:			# of the above pattern
					\d+(?::\d+)?
					|
					[a-z]+
				)
			)*
		""", service, re.VERBOSE):
			raise CommandError(
				self, f'"{service}" is not a valid service specification'
			)

		# Make sure blank strings are None for flags and comment
		flags = blank_str_to_None(flags)
		comment = blank_str_to_None(comment)

		for scope_mapping in scope_mappings:
			# Check that the rule name is unique for the scope
			if self.db.count("""
		 		(firewall_rules.id) FROM firewall_rules,scope_map
				WHERE firewall_rules.scope_map_id = scope_map.id
				AND firewall_rules.name = %s
				AND scope_map.scope = %s
				AND scope_map.appliance_id <=> %s
				AND scope_map.os_id <=> %s
				AND scope_map.environment_id <=> %s
				AND scope_map.node_id <=> %s
			""", (name, *scope_mapping)) != 0:
		 		raise CommandError(self, f'rule named "{name}" already exists')

			# And that the rule is unique for the scope
			if self.db.count("""
		 		(firewall_rules.id) FROM firewall_rules,scope_map
				WHERE firewall_rules.scope_map_id = scope_map.id
				AND firewall_rules.table_type = %s
				AND firewall_rules.chain = %s
				AND firewall_rules.action = %s
				AND firewall_rules.service = %s
				AND firewall_rules.protocol = %s
				AND firewall_rules.in_subnet_id <=> %s
				AND firewall_rules.out_subnet_id <=> %s
				AND firewall_rules.flags <=>%s
				AND scope_map.scope = %s
				AND scope_map.appliance_id <=> %s
				AND scope_map.os_id <=> %s
				AND scope_map.environment_id <=> %s
				AND scope_map.node_id <=> %s
			""", (
				table_type, chain, action, service, protocol, in_subnet_id,
				out_subnet_id, flags, *scope_mapping
			)) != 0:
				raise CommandError(self, 'firewall rule already exists')

		# Everything looks good, add the new rules
		for scope_mapping in scope_mappings:
			# First add the scope mapping for the new rule
			self.db.execute("""
				INSERT INTO scope_map(
					scope, appliance_id, os_id, environment_id, node_id
				)
				VALUES (%s, %s, %s, %s, %s)
			""", scope_mapping)

			# Then add the rule itself
			self.db.execute("""
				INSERT INTO firewall_rules(
					scope_map_id, name, table_type, chain, action, service,
					protocol, in_subnet_id, out_subnet_id, flags, comment
				)
				VALUES (LAST_INSERT_ID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""", (
				name, table_type, chain, action, service, protocol, in_subnet_id,
				out_subnet_id, flags, comment
			))
