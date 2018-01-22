# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.5  2010/09/07 23:52:55  bruno
# star power for gb
#
# Revision 1.4  2010/05/11 22:28:16  bruno
# more tweaks
#
# Revision 1.3  2010/05/07 23:13:32  bruno
# clean up the help info for the firewall commands
#
# Revision 1.2  2010/05/04 22:04:15  bruno
# more firewall commands
#
# Revision 1.1  2010/04/30 22:07:16  bruno
# first pass at the firewall commands. we can do global and host level
# rules, that is, we can add, remove, open (calls add), close (also calls add),
# list and dump the global rules and the host-specific rules.
#
#

import json
import stack.commands

class Plugin(stack.commands.Plugin):
	"""
	Generates firewall rules based on scope
	"""

	def formatRule(self, name, table, inid, outid, service, protocol,
			chain, action, flags, comment, source, rule_type):

		if inid == 0:
			network = 'all'
		else:
			network = self.owner.getNetworkName(inid)
		if outid == 0:
			output_network = 'all'
		else:
			output_network = self.owner.getNetworkName(outid)

		rule = (name, service, table, protocol, chain, action, network,
                        output_network, flags, comment, source, rule_type)

		if action == 'ACCEPT':
			self.accept_rules.append(rule)
		elif action == 'REJECT':
			self.reject_rules.append(rule)
		elif rule_type == 'const':
			self.intrinsic_rules.append(rule)
		else:
			self.other_rules.append(rule)

	# Add firewall rules for pxe=True networks
	def addIntrinsicRules(self):
		LUDICROUS_PORT = 3285

		# Get list of networks with pxe=True
		netList = self.owner.call('list.network', ['pxe=True'])

		for network in netList:
			protocol = 'all'
			chain = 'all'
			output_network = ''
			flags = ''
			service_list = ['http', 'https', 'tftp', 'dhcp', 'ssh', str(LUDICROUS_PORT)]
			for service in service_list:
				net_name = network['network']
				comment = 'Accept all %s traffic on %s network - Intrinsic rule' % (service, net_name)
				net_service = '%s-%s' % (net_name, service)

				self.intrinsic_rules.append((net_service + '-INPUT', 'filter', service,
					protocol, 'INPUT', 'ACCEPT', net_name, output_network,
					flags, comment, 'G', 'const'))

				self.intrinsic_rules.append((net_service + '-OUTPUT', 'filter', service,
					protocol, 'OUTPUT', 'ACCEPT', net_name, output_network,
					flags, comment, 'G', 'const'))

				self.intrinsic_rules.append((net_service + '-FORWARD', 'filter', service,
					protocol, 'FORWARD', 'ACCEPT', net_name, output_network,
					flags, comment, 'G', 'const'))

	def printOutput(self, colName):
		output_actions = self.intrinsic_rules + self.accept_rules + self.other_rules + self.reject_rules
		for action in output_actions:
			(name, service, table, protocol, chain, action, network,
                        output_network, flags, comment, source, rule_type) = action

			self.owner.addOutput(colName, (name, table, service,
				protocol, chain, action, network, output_network,
				flags, comment, source, rule_type))

	def empty_lists(self):
		del self.accept_rules[:]
		del self.reject_rules[:]
		del self.other_rules[:]
		del self.intrinsic_rules[:]

	def global_firewall(self, args, host=''):
		self.owner.db.execute("""select insubnet, outsubnet, service,
			protocol, chain, action, flags, comment, tabletype,
			name from global_firewall""")

		for i, o, s, p, c, a, f, cmt, tt, n in self.db.fetchall():
			self.formatRule(n, tt, i, o, s, p, c, a, f, cmt, 
				'G', 'var')
		if not host:
			self.printOutput('')
			self.owner.endOutput(header=['', 'name', 'table', 'service',
				'protocol', 'chain', 'action', 'network',
				'output-network', 'flags', 'comment', 
				'source', 'type'])

	def os_firewall(self, args, host=''):
		if host:
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from os_firewall where os =
				(select os from nodes where name = '%s')"""
				% (host))

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(n, tt, i, o, s, p, c, a, f,
					cmt, 'O', 'var')
		else:
			for os in self.owner.getOSNames(args):
				self.db.execute("""select name, tabletype, insubnet,
					outsubnet, service, protocol, chain, action,
					flags, comment from os_firewall
					where os = '%s' """ % os)

				for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
					self.formatRule(n, tt, i, o, s, p, c, a, f,
						cmt, 'O', 'var')

				self.printOutput(os)
				self.empty_lists()

			self.owner.endOutput(header=['os', 'name', 'table', 'service',
				'protocol', 'chain', 'action', 'network',
				'output-network', 'flags', 'comment', 'source', 
				'type'], trimOwner=0)

	def appliance_firewall(self, args, host=''):
		if host:
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from appliance_firewall where
				appliance =
				(select appliance from nodes where name = '%s')
				""" % host)

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(n, tt, i, o, s, p, c, a, f,
					cmt, 'A', 'var')
		else:
			for app in self.owner.getApplianceNames(args):
				self.db.execute("""select insubnet, outsubnet,
					service, protocol, chain, action, flags,
					comment, name, tabletype from appliance_firewall where
					appliance = (select id from appliances where
					name = '%s')""" % app)
				for i, o, s, p, c, a, f, cmt, n, tt in self.db.fetchall():
					self.formatRule(n, tt, i, o, s, p, c, a, f,
						cmt, 'A', 'var')

				self.printOutput(app)
				self.empty_lists()

			self.owner.endOutput(header=['appliance', 'name', 'table',
				'service', 'protocol', 'chain', 'action', 'network',
				'output-network', 'flags', 'comment', 'source',
				'type'], trimOwner=0)

	def host_firewall(self, args):
		for host in self.owner.getHostnames(args):

			# global
			self.global_firewall(args, host)

			# os
			self.os_firewall(args, host)

			# appliance
			self.appliance_firewall(args, host)

			# host
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from node_firewall where node =
				(select id from nodes where name = '%s')"""
				% (host))

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(n, tt, i, o, s, p, c, a, f,
					cmt, 'H', 'var')

			# Add Intrinsic rules
			self.addIntrinsicRules()

			self.printOutput(host)
			self.empty_lists()

		self.owner.endOutput(header=['host', 'name', 'table', 'service',
			'protocol', 'chain', 'action', 'network',
			'output-network', 'flags', 'comment', 'source', 'type' ])

	lookup = {      'global'    : global_firewall,
			'os'        : os_firewall,
			'appliance' : appliance_firewall,
			'host'      : host_firewall
		}

	accept_rules = []
	reject_rules = []
	intrinsic_rules = []
	other_rules = []

	def run(self, args):
		self.owner.beginOutput()
		self.lookup[self.owner.scope](self, args=args)
