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
		self.addOutput(host, ':FORWARD DROP [0:0]')
		self.addOutput(host, ':OUTPUT ACCEPT [0:0]')

	def printRules(self, host, table, rules):
		if len(rules) == 0 and table != 'filter':
			return
		self.addOutput(host, '*%s' % table)
		if table == 'filter':
			self.getPreamble(host)
		for rule in rules:
			s = '-A %s' % rule['chain']
			if rule['network'] != 'all' and \
				rule['network'] is not None:
				query = "select nt.device from networks nt," +\
					"nodes n, subnets s where " +\
					"s.name='%s' and " % (rule['network']) +\
					"n.name='%s' and " % host +\
					"nt.node=n.id and nt.subnet=s.id"
				rows = self.db.execute(query)
				if rows:
					interface = self.db.fetchone()[0]
					s += ' -i %s' % interface
				else:
					continue
			if rule['output-network'] != 'all' and \
				rule['output-network'] is not None:
				query = "select nt.device from networks nt," +\
					"nodes n, subnets s where " +\
					"s.name='%s' and " % (rule['output-network']) +\
					"n.name='%s' and " % host +\
					"nt.node=n.id and nt.subnet=s.id"
				rows = self.db.execute(query)
				if rows:
					interface = self.db.fetchone()[0]
					s += ' -o %s' % interface

			s += ' -j %s' % rule['action']

			if rule['protocol'] != 'all' and \
				rule['protocol'] is not None:
				s += ' -p %s' % rule['protocol']
			if rule['flags'] is not None:
				s += ' %s' % rule['flags']
			if rule['service'] != 'all' and \
				rule['service'] is not None:
				if rule['protocol'] == 'all':
					tmp_rule = s
					s = "%s -p tcp --dport %s\n" % (tmp_rule, rule['service'])
					s += "%s -p udp --dport %s" % (tmp_rule, rule['service'])
				else:
					s += ' --dport %s' % rule['service']

			if rule['comment'] is not None:
				self.addOutput(host, '# %s' % rule['comment'])
			else:
				comment = "# %s rule" % (rule['action'])
				if rule['network'] == 'all':
					comment =  comment + " for all networks"
				elif rule['network'] is not None:
					comment =  comment + " for %s network" % (rule['network'])

				self.addOutput(host, comment)
			self.addOutput(host, s)
			self.addOutput(host, '')

		self.addOutput(host, 'COMMIT')
				
	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			s = '<stack:file stack:name="/etc/sysconfig/iptables" stack:perms="500">'
			self.addOutput(host, s)
			# First, get a list of all rules for every host,
			# fully resolved
			rules = self.call('list.host.firewall', [host])

			# Separate the rules into intrinsic rules, accept rules, reject rules,
			# and other rules.
			intrinsic_rules = []
			accept_rules = []
			other_rules = []
			reject_rules = []

			while rules:
				rule = rules.pop()
				if rule['type'] == 'const':
					intrinsic_rules.append(rule)
				elif rule['action'] == 'ACCEPT':
					accept_rules.append(rule)
				elif rule['action'] == 'REJECT':
					reject_rules.append(rule)
				elif rule['action'] == 'DROP':
					reject_rules.append(rule)
				else:
					other_rules.append(rule)

			# order the rules by Intrinsic, ACCEPT, OTHER, and REJECT
			rules = intrinsic_rules + accept_rules + other_rules + reject_rules

			# Separate rules by the tables that they belong to.
			# They can belong to the filter, nat, raw, and mangle tables.
			tables = {}
			
			while rules:
				rule = rules.pop(0)
				table = rule['table']
				if table not in tables:
					tables[table] = []
				tables[table].append(rule)
			# Generate rules for each of the table types
			for tt in ['filter', 'nat', 'raw', 'mangle']:
				# Finally print all the rules that are present
				# in each table. These rules are already sorted
				# so no further sorting is necessary
				if tt in tables:
					self.printRules(host, tt, tables[tt])

			#
			# default reject rules
			#
			#rule = self.buildRule(None, None, None, '0:1023',
			#	'tcp', 'REJECT', 'INPUT', None, None)
			#self.addOutput(host, rule)

			#rule = self.buildRule(None, None, None, '0:1023',
			#	'udp', 'REJECT', 'INPUT', None, None)
			#self.addOutput(host, rule)

			self.addOutput(host, '</stack:file>')

		self.endOutput(padChar='', trimOwner=True)

