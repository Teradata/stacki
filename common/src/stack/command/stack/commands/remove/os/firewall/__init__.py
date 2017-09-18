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


class Command(stack.commands.remove.os.command,
	stack.commands.remove.firewall.command):

	"""
	Remove a firewall rule for an OS type. To remove
	a rule, one must supply the name of the rule.

	<arg type='string' name='os' repeat='1'>
	Name of an OS type (e.g., "linux", "sunos").
	</arg>

	<param name="rulename" type="string" optional='0'>
	Name of the OS-specific rule
	</param>
	"""

	def run(self, params, args):
		(rulename, ) = self.fillParams([ ('rulename', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'os')
		
		for os in self.getOSNames(args):
			sql = """os='%s'""" % (os)

			self.deleteRule('os_firewall', rulename, sql)
