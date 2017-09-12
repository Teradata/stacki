# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands
import stack.commands.add
import stack.commands.add.firewall
from stack.exception import ArgRequired


class Command(stack.commands.add.firewall.command,
	stack.commands.add.appliance.command):

	"""
	Add a firewall rule for an appliance type.

	<arg type='string' name='appliance' repeat='1'>
	Appliance type (e.g., "backend").
	</arg>

	<param type='string' name='service' require='1'>
	The service identifier, port number or port range. For example
	"www", 8080 or 0:1024.
	To have this firewall rule apply to all services, specify the
	keyword 'all'.
	</param>

	<param type='string' name='protocol' require='1'>
	The protocol associated with the service. For example, "tcp" or "udp".
	To have this firewall rule apply to all protocols, specify the
	keyword 'all'.
	</param>
	
	<param type='string' name='network'>
	The network for this rule. This is a named network
	(e.g., 'private') and must be one listed by the command
	'stack list network'.
	To have this firewall rule apply to all networks, specify the
	keyword 'all'.
	</param>

	<param type='string' name='output-network'>
	The output network for this rule. This is a named
	network (e.g., 'private') and must be one listed by the command
	'stack list network'.
	</param>

	<param type='string' name='chain' require='1'>
	The iptables 'chain' for this this rule (e.g., INPUT, OUTPUT, FORWARD).
	</param>

	<param type='string' name='action' require='1'>
	The iptables 'action' this rule (e.g., ACCEPT, REJECT, DROP).
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

	<example cmd='add appliance firewall login network=private service="all" protocol="all" action="ACCEPT" chain="FORWARD"'>
	Accept all services and all protocols on the private network for the
	FORWARD chain.
	If 'eth0' is associated with the private network on a login appliance,
	then this will be translated as the following iptables rule:
	"-A FORWARD -i eth0 -j ACCEPT"
	</example>

	<example cmd='add appliance firewall login network=all service="8649" protocol="udp" action="REJECT" chain="INPUT"'>
	Reject UDP packets with a destination port of 8649 on all networks for
	the INPUT chain.
	On login appliances, this will be translated into the following
	iptables rule:
	"-A INPUT -p udp --dport 8649 -j REJECT"
	</example>
	"""

	def run(self, params, args):
		
		(service, network, outnetwork, chain, action, protocol, flags,
		 comment, table, rulename) = self.doParams()

		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		apps = self.getApplianceNames(args)

		for app in apps:
			sql = """appliance = (select id from appliances where
				name = '%s') and""" % app

			self.checkRule('appliance_firewall', sql, service,
				network, outnetwork, chain, action, protocol,
				flags, comment, table, rulename)

		#
		# all the rules are valid, now let's add them
		#
		for app in apps:
			sql = """(select id from appliances where
				name='%s'), """ % app

			self.insertRule('appliance_firewall', 'appliance, ',
				sql, service, network, outnetwork, chain,
				action, protocol, flags, comment, table, rulename)

