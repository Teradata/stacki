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

from collections import defaultdict

import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Create a report that outputs the firewall rules for a host.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='report host firewall backend-0-0'>
	Create a report of the firewall rules for backend-0-0.
	</example>
	"""

	def getPreamble(self, host):
		self.addOutput(host, ':INPUT ACCEPT [0:0]')
		self.addOutput(host, ':FORWARD ACCEPT [0:0]')
		self.addOutput(host, ':OUTPUT ACCEPT [0:0]')
		self.addOutput(host, '')

	def expandRules(self, lines, parameter, items):
		return [
			f'{line} {parameter} {item}'
			for line in lines
			for item in items
		]

	def printRules(self, host, table, rules):
		if len(rules) == 0 and table != 'filter':
			return

		# Blank line to seperate table types
		if table != 'filter':
			self.addOutput(host, '')

		# Output the table type and the filter preamble
		self.addOutput(host, f'*{table}')
		if table == 'filter':
			self.getPreamble(host)

		# Create a mapping of networks to interfaces for this host
		network_to_interfaces = defaultdict(list)
		for row in self.call('list.host.interface', [host]):
			network_to_interfaces[row['network']].append(row['interface'])

		for rule in rules:
			if rule['comment']:
				comment = f"# {rule['comment']}"
			else:
				comment = f"# {rule['action']} rule"

				if rule['network'] == 'all':
					comment += ' for all networks'
				elif rule['network']:
					comment += f" for {rule['network']} network"

			# Base of the rule
			line = f"-A {rule['chain']} -j {rule['action']}"

			if rule['flags']:
				line += f" {rule['flags']}"

			# A single input rule can map to multiple lines in iptables
			lines = [line]

			# If the 'protocol' is 'all' and if there is a 'service'
			# defined, then we need two rules: one with '-p tcp' and
			# one with '-p udp'

			service = None
			if rule['service'] != 'all' and rule['service']:
				service = rule['service']

			if rule['protocol'] and rule['protocol'] != 'all':
				lines = self.expandRules(lines, '-p', [rule['protocol']])
			elif rule['protocol'] == 'all' and service:
				lines = self.expandRules(lines, '-p', ['tcp', 'udp'])

			# Order is important here: '--dport' must come immediately after '-p'
			if service:
				lines = self.expandRules(lines, '--dport', [service])

			if rule['network'] and rule['network'] != 'all':
				# Skip the rule if there is no interface on this network
				if not network_to_interfaces[rule['network']]:
					continue

				lines = self.expandRules(
					lines, '-i', network_to_interfaces[rule['network']]
				)

			if rule['output-network'] and rule['output-network'] != 'all':
				# Skip the rule if there is no interface on this network
				if not network_to_interfaces[rule['output-network']]:
					continue

				lines = self.expandRules(
					lines, '-o', network_to_interfaces[rule['output-network']]
				)

			# Output the rules
			self.addOutput(host, comment)

			for line in lines:
				self.addOutput(host, line)

			self.addOutput(host, '')

		self.addOutput(host, 'COMMIT')

	def _rule_sorter(self, rule):
		# Sort the rules by: Intrinsic, Accept, Other, Drop, and Reject
		if rule['type'] == 'const':
			# Intrinsic
			return 0
		elif rule['action'] == 'ACCEPT':
			return 1
		elif rule['action'] == 'DROP':
			return 3
		elif rule['action'] == 'REJECT':
			return 4

		# Other
		return 2

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			self.addOutput(
				host,
				'<stack:file stack:name="/etc/sysconfig/iptables" stack:perms="500">'
			)

			# Get the rules for our host
			rules = self.call('list.host.firewall', [host])

			# Run through the rules in sorted order and seperate them by
			# table type: filter, nat, raw, and mangle tables
			tables = defaultdict(list)
			for rule in sorted(rules, key=self._rule_sorter):
				tables[rule['table']].append(rule)

			# Generate rules for each of the table types
			for table in ('filter', 'nat', 'raw', 'mangle'):
				self.printRules(host, table, tables[table])

			self.addOutput(host, '</stack:file>')

		self.endOutput(padChar='', trimOwner=True)
