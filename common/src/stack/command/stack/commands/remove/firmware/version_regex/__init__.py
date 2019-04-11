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
	Removes firmware version_regexes from the stacki database.

	<arg type='string' name='version_regexes'>
	One or more version_regexes to remove.
	</arg>

	<example cmd="remove firmware version_regex mellanox_version intel_version">
	Removes the mellanox_version and intel_version version_regexes from the database.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
