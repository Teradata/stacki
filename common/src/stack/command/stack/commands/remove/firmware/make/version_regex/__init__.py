# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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

class Command(stack.commands.remove.firmware.command):
	"""
	Disassociates firmware version_regexes from one or more makes.

	<arg type='string' name='makes'>
	One or more makes to disassociate from a version_regex.
	</arg>

	<example cmd="remove firmware make version_regex Mellanox Intel">
	Disassociates the Mellanox and Intel makes from any version_regexes that were set for them.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
