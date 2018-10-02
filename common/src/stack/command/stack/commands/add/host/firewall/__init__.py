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
import stack.commands.add
import stack.commands.add.firewall
from stack.exception import ArgRequired, CommandError

class Command(stack.commands.add.firewall.command,
	stack.commands.add.host.command):
	"""
	Add a firewall rule for the specified hosts.

	<arg type='string' name='host' repeat='1'>
	Host name of machine
	</arg>

	<param type='string' name='service' optional='0'>
	The service identifier, port number or port range. For example
	"www", 8080 or 0:1024.
	To have this firewall rule apply to all services, specify the
	keyword 'all'.
	</param>

	<param type='string' name='protocol' optional='0'>
	The protocol associated with the service. For example, "tcp" or "udp".
	To have this firewall rule apply to all protocols, specify the
	keyword 'all'.
	</param>
	
	<param type='string' name='network'>
	The network this rule service should be applied to. This is a named
	network (e.g., 'private') and must be one listed by the command
	'rocks list network'.
	To have this firewall rule apply to all networks, specify the
	keyword 'all'.
	</param>

	<param type='string' name='output-network' optional='1'>
	The output network this rule should be applied to. This is a named
	network (e.g., 'private') and must be one listed by the command
	'rocks list network'.
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

	<example cmd='add host firewall localhost network=private service="all" protocol="all" action="ACCEPT" chain="FORWARD"'>
	Accept all services and all protocols from the private network on
	the FORWARD chain.
	If 'eth0' is associated with the private network, then this will
	be translated as the following iptables rule:
	"-A FORWARD -i eth0 -j ACCEPT".
	</example>

	<example cmd='add host firewall localhost network=all service="40000"
	protocol="tcp" action="REJECT" chain="INPUT"'>
	Reject TCP packets that are destined for port 40000 on all networks
	on the INPUT chain.
	This will be translated into the following rule:
	"-A INPUT -p tcp --dport 40000 -j REJECT"
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)
		
		(service, network, outnetwork, chain, action, protocol, flags,
			comment, table, rulename) = self.doParams()

		# Make sure we have a new rule
		for host in hosts:
			if self.db.count("""(*) from node_firewall where
				node = (select id from nodes where name = %s) and
				service = %s and action = %s and chain = %s and
				if (%s is NULL, insubnet is NULL, insubnet = %s) and
				if (%s is NULL, outsubnet is NULL, outsubnet = %s) and
				if (%s is NULL, protocol is NULL, protocol = %s) and
				if (%s is NULL, flags is NULL, flags = %s)""",
				(host, service, action, chain, network, network, outnetwork,
				outnetwork, protocol, protocol, flags, flags)
			) > 0:
				raise CommandError(self, 'firewall rule already exists')

		# Now let's add them
		for host in hosts:
			self.db.execute("""insert into node_firewall
				(node, insubnet, outsubnet, service, protocol,
				action, chain, flags, comment, tabletype, name)
				values ((select id from nodes where name=%s),
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
				(host, network, outnetwork,	service, protocol, action,
				chain, flags, comment, table, rulename)
			)
