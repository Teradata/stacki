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
from stack.mq import ports as rmqports

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

		rule = (name, table, service, protocol, chain, action, network,
                        output_network, flags, comment, source, rule_type)

		self.resolved_rules[name] = rule

	# Add firewall rules for pxe=True networks.
	# The intrinsic rules are as follows
	# Frontend allows Ingress traffic on HTTP, HTTPS,
	# TFTP, LUDICROUS, RMQ traffic, and DNS traffic 
	# Backends allow Ingress traffic on SSH and RMQ ports
	# from frontend.
	def addIntrinsicRules(self, host):
		frontend = False
		if  self.owner.getHostAttr(host, 'appliance') == 'frontend':
			frontend = True

		LUDICROUS_PORT = 3825

		# Get list of networks with pxe=True
		netList = self.owner.call('list.network')

		frontend_ips = self.owner.call('list.host.interface', ['a:frontend'])
		for network in netList:
			protocol = 'tcp'
			chain = 'all'
			output_network = ''
			flags = ''
			net_name = network['network']
			pxe = network['pxe']
			dns = network['dns']
			if frontend:
				if pxe:
					service_list = ['http', 'https', str(LUDICROUS_PORT),
						str(rmqports.subscribe), str(rmqports.control) ]
					comment = 'Accept Stacki traffic on %s network - Intrinsic rule' % ( net_name)
					flags = '-m multiport'
					self.intrinsic_rules.append(('STACKI-INSTALLATION-%s' % net_name.upper(), 'filter', ','.join(service_list),
						protocol, 'INPUT', 'ACCEPT', net_name, output_network,
						flags, comment, 'G', 'const'))
					service_list = ['tftp', 'bootps', 'bootpc']
					comment = 'Accept UDP traffic for TFTP on %s network - Intrinsic rule' % ( net_name)
					flags = '-m multiport'
					self.intrinsic_rules.append(('STACKI-TFTP-%s' % net_name.upper(), 'filter', ','.join(service_list),
						'udp', 'INPUT', 'ACCEPT', net_name, output_network,
						flags, comment, 'G', 'const'))
					comment = "Accept UDP traffic for RMQ publisher over %s network - Intrinsic Rule" % (net_name)
					flags = ''
					self.intrinsic_rules.append(('STACKI-MQ-PUBLISH-PORT-%s' % net_name.upper(), 'filter', str(rmqports.publish),
						'udp', 'INPUT', 'ACCEPT', net_name, output_network,
						flags, comment , 'G', 'const'))
				if dns:
					flags = '-s %s/%s' % (network['address'], network['mask'])
					comment = "Accept DNS traffic over %s network - Intrinsic Rule" % (net_name)
					self.intrinsic_rules.append(('STACKI-DNS-%s' % net_name.upper(), 'filter', 'domain',
						'all', 'INPUT', 'ACCEPT', net_name, output_network,
						flags, comment , 'G', 'const'))
			else:
				if pxe:
					f = lambda x: x['network'] == net_name 
					fip = list(filter(f, frontend_ips))
					if len(fip):
						frontend_ip_flag = '-s %s' % fip[0]['ip']
					else:
						frontend_ip_flag = ''
					flags = '%s' % frontend_ip_flag
					service_list = ['ssh', str(rmqports.control)]
					comment = 'Accept all frontend traffic on %s network - Intrinsic rule' % ( net_name)
					self.intrinsic_rules.append(('STACKI-FRONTEND-INGRESS', 'filter', 'all',
						'all', 'INPUT', 'ACCEPT', net_name, output_network,
						flags, comment, 'G', 'const'))


	def categorizeRules(self):
		for rulename in self.resolved_rules:
			rule = self.resolved_rules[rulename]
			action=rule[5]
			rule_type = rule[11]
			if action == 'ACCEPT':
				self.accept_rules.append(rule)
			elif action == 'REJECT':
				self.reject_rules.append(rule)
			elif rule_type == 'const':
				self.intrinsic_rules.append(rule)
			else:
				self.other_rules.append(rule)
		

	def printOutput(self, colName):
		output_actions = self.intrinsic_rules + self.accept_rules + self.other_rules + self.reject_rules
		for action in output_actions:
			(name, table, service, protocol, chain, action, network,
                        output_network, flags, comment, source, rule_type) = action

			self.owner.addOutput(colName, (name, table, service,
				protocol, chain, action, network, output_network,
				flags, comment, source, rule_type))

	def empty_lists(self):
		del self.accept_rules[:]
		del self.reject_rules[:]
		del self.other_rules[:]
		del self.intrinsic_rules[:]
		self.resolved_rules = {}

	def global_firewall(self, args, host=''):
		self.owner.db.execute("""select insubnet, outsubnet, service,
			protocol, chain, action, flags, comment, tabletype,
			name from global_firewall""")

		for i, o, s, p, c, a, f, cmt, tt, n in self.db.fetchall():
			self.formatRule(n, tt, i, o, s, p, c, a, f, cmt, 
				'G', 'var')
		if not host:
			self.categorizeRules()
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

				self.categorizeRules()
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

				self.categorizeRules()
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
			self.addIntrinsicRules(host)

			self.categorizeRules()

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

	resolved_rules = {}

	def run(self, args):
		self.owner.beginOutput()
		self.lookup[self.owner.scope](self, args=args)
