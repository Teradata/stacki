# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.add.environment.command):
	"""
	Add a firewall rule for an environment.

	<arg type='string' name='environment' repeat='1' optional='0'>
	An environment name.
	</arg>

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
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'environment')

		self.command('add.firewall', self._argv + ['scope=environment'], verbose_errors = False)
		return self.rc
