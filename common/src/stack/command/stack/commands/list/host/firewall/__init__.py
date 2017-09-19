# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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


class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.list.host.command):
	"""
	List the current firewall rules for the named hosts.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the 
	firewall rules for all the known hosts are listed.
	</arg>
	"""

	def formatRule(self, rules, name, table, inid, outid, service,
			protocol, chain, action, flags, comment, source):

		if inid == 0:
			network = 'all'
		else:
			network = self.getNetworkName(inid)
		if outid == 0:
			output_network = 'all'
		else:
			output_network = self.getNetworkName(outid)

		rules[name] = (service, table, protocol, chain, action, network,
			output_network, flags, comment, source)


	def run(self, params, args):
		self.beginOutput()

		for host in self.getHostnames(args):
			rules = {}

			# global
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from global_firewall""")

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'G')

			# os
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from os_firewall where os =
				(select os from nodes where name = '%s')"""
				% (host))

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'O')

			# appliance
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from appliance_firewall where
				appliance =
				(select appliance from nodes where name = '%s')
				""" % host)
			
			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'A')

			# host
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from node_firewall where node =
				(select id from nodes where name = '%s')"""
				% (host))

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'H')

			#
			# output the 'ACCEPT' actions first, the 'REJECT'
			# actions last and all the others in the middle
			#
			for n in rules:
				s, tt, p, c, a, i, o, f, cmt, source = rules[n]
				if a == 'ACCEPT':
					self.addOutput(host, (n, tt, s, p, c, a, i,
						o, f, cmt, source))

			for n in rules:
				s, tt, p, c, a, i, o, f, cmt, source = rules[n]
				if a not in [ 'ACCEPT', 'REJECT' ]:
					self.addOutput(host, (n, tt, s, p, c, a, i,
						o, f, cmt, source))

			for n in rules:
				s, tt, p, c, a, i, o, f, cmt, source = rules[n]
				if a == 'REJECT':
					self.addOutput(host, (n, tt, s, p, c, a, i,
						o, f, cmt, source))

		self.endOutput(header=['host', 'name', 'table', 'service',
			'protocol', 'chain', 'action', 'network',
			'output-network', 'flags', 'comment', 'source' ])

