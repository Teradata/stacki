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

import string
import uuid

import stack.commands
from stack.exception import CommandError, ParamRequired, ParamError


class command(stack.commands.HostArgumentProcessor,
	stack.commands.add.command):
	
	def serviceCheck(self, service):
		#
		# a service can look like:
		#
		#	reserved words: all
		#       named service: ssh
		#       specific port: 8069
		#       port range: 0:1024
		#	comma-separated combination of the above
		#
		if service == 'all':
			#
			# valid
			#
			return

		for s in service.split(','):

			if s[0] in string.digits:
				#
				# if the first character is a number, then assume
				# this is a port or port range:
				#
				ports = s.split(':')
				if len(ports) > 2:
					msg = 'port range "%s" is invalid. ' % s
					msg += 'it must be "integer:integer"'
					raise CommandError(self, msg)

				for a in ports:
					try:
						int(a)
					except:
						msg = 'port specification "%s" ' % \
							s
						msg += 'is invalid. '
						msg += 'it must be "integer" or '
						msg += '"integer:integer"'
						raise CommandError(self, msg)
				
		#
		# if we made it here, then the service definition looks good
		#
		return


	def doParams(self):

		(service, network, outnetwork, chain, action, protocol, flags,
			comment, table, rulename) = self.fillParams([
				('service',		None,	True),
				('network',		None),
				('output-network',	None),
				('chain',		None,	True),
				('action',		None,	True),
				('protocol',		None,	True),
				('flags',		None),
				('comment',		None),
				('table',		'filter'),
				('rulename',		None),
			])
		
		if not network and not outnetwork:
			raise ParamRequired(self, ('network', 'output-network'))

		if table not in ['filter', 'raw', 'mangle', 'nat']:
			raise ParamError(self, 'table', 'is not valid')

		#
		# check if the network exists
		#
		if network == 'all':
			network = 0
		elif network:
			rows = self.db.select('id from subnets where name = %s', (network,))

			if len(rows) == 0:
				raise CommandError(self, 'network "%s" not in the database. Run "stack list network" to get a list of valid networks.' % network)

			network = rows[0][0]
		elif network == "":
			network = None
		
		if outnetwork == 'all':
			outnetwork = 0
		elif outnetwork:
			rows = self.db.select('id from subnets where name = %s', (outnetwork,))

			if len(rows) == 0:
				raise CommandError(self, 'output-network "%s" not in the database. Run "stack list network" to get a list of valid networks.' % outnetwork)

			outnetwork = rows[0][0]
		elif outnetwork == "":
			outnetwork = None
		
		self.serviceCheck(service)

		action = action.upper()
		chain = chain.upper()

		# Make sure empty strings are None
		if protocol == "":
			protocol = None

		if flags == "":
			flags = None
		
		if comment == "":
			comment = None

		if not rulename:
			rulename = str(uuid.uuid1())

		return (service, network, outnetwork, chain, action,
			protocol, flags, comment, table, rulename)


class Command(command):
	"""
	Add a global firewall rule for the all hosts in the cluster.

	<param type='string' name='service' optional='0'>
	The service identifier, port number or port range. For example
	"www", 8080 or 0:1024.
	To have this firewall rule apply to all services, specify the
	keyword 'all'.
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
	To have this firewall rule apply to all networks, specify the
	keyword 'all'.
	</param>

	<param type='string' name='output-network' optional='1'>
	The output network this rule should be applied to. This is a named
	network (e.g., 'private') and must be one listed by the command
	'stack list network'.
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

	<example cmd='add firewall network=private service="all" protocol="all" action="ACCEPT" chain="INPUT"'>
	Accept all protocols and all services on the private network on the
	INPUT chain.
	If 'eth0' is the private network, then this will be translated as
	the following iptables rule:
	"-A INPUT -i eth0 -j ACCEPT"
	</example>
	"""
	def run(self, params, args):
		
		(service, network, outnetwork, chain, action, protocol, flags,
		 comment, table, rulename) = self.doParams()

		# Make sure we have a new rule
		if self.db.count(
			'(*) from global_firewall where name=%s',
			(rulename,)
		) > 0:
			raise CommandError(self, f'Rule with rulename "{rulename}" already exists')
		
		# Now let's add them
		self.db.execute("""insert into global_firewall
			(insubnet, outsubnet, service, protocol,
			action, chain, flags, comment, tabletype, name)
			values (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s)""",
			(network, outnetwork, service, protocol, action,
			chain, flags, comment, table, rulename)
		)
