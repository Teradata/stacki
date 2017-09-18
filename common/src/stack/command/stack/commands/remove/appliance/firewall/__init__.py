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


class Command(stack.commands.remove.appliance.command,
	stack.commands.remove.firewall.command):

	"""
	Remove a firewall service rule for an appliance type.
	To remove the rule, you must supply the name of the rule.

	<arg type='string' name='appliance' repeat='1'>
	Name of an appliance type (e.g., "backend").
	</arg>

	<param type='string' name='rulename' optional='0'>
	Name of the Appliance-specific rule
	</param>

	"""

	def run(self, params, args):
		(rulename, ) = self.fillParams([ ('rulename', None, True) ])

		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		for app in self.getApplianceNames(args):
			sql = """appliance = (select id from appliances where
				name = '%s')""" % (app)

			self.deleteRule('appliance_firewall', rulename, sql)

