# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import stack.commands
import stack.commands.remove.firewall
from stack.exception import ArgRequired


class Command(stack.commands.remove.host.command,
	stack.commands.remove.firewall.command):

	"""
	Remove a firewall rule for a host. To remove a rule,
	you must supply the name of the rule. The Rule names may
	be obtained by running "rocks list host firewall"

	<arg type='string' name='host' repeat='1'>
	Name of a host machine.
	</arg>

	<param type='string' name='rulename' optional='0'>
	Name of host-specific rule
	</param>

	"""

	def run(self, params, args):
		(rulename, ) = self.fillParams([ ('rulename', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'host')

		for host in self.getHostnames(args):
			sql = """node = (select id from nodes where
				name = '%s')""" % (host)

			self.deleteRule('node_firewall', rulename, sql)

