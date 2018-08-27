# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.commands.add
import stack.commands.add.firewall
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.add.firewall.command,
	stack.commands.add.environment.command):

	"""
	Add a firewall rule for an environment.

	<arg type='string' name='environment' repeat='1'>
	An environment name.
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

	<param type='string' name='chain' optional='0'>
	The iptables 'chain' for this this rule (e.g., INPUT, OUTPUT, FORWARD).
	</param>

	<param type='string' name='action' optional='0'>
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
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		envs = self.getEnvironmentNames(args)

		(service, network, outnetwork, chain, action, protocol, flags,
		 comment, table, rulename) = self.doParams()

		# Make sure we have a new rule
		for env in envs:
			if self.db.select("""count(*) from environment_firewall where
				environment = (select id from environments where name = %s) and
				service = %s and action = %s and chain = %s and
				if (%s is NULL, insubnet is NULL, insubnet = %s) and
				if (%s is NULL, outsubnet is NULL, outsubnet = %s) and
				if (%s is NULL, protocol is NULL, protocol = %s) and
				if (%s is NULL, flags is NULL, flags = %s)""",
				(env, service, action, chain, network, network, outnetwork,
				outnetwork, protocol, protocol, flags, flags)
			)[0][0] > 0:
				raise CommandError(self, 'firewall rule already exists')

		# Now let's add them
		for env in envs:
			self.db.execute("""insert into environment_firewall
				(environment, insubnet, outsubnet, service, protocol,
				action, chain, flags, comment, tabletype, name)
				values ((select id from environments where name = %s),
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
				(env, network, outnetwork, service, protocol, action,
				chain, flags, comment, table, rulename)
			)
