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

class Command(stack.commands.set.firmware.command):
	"""
	Associates a firmware version_regex with one or more makes.

	<arg type='string' name='makes'>
	One or more makes to associate the version_regex with.
	</arg>

	<param type='string' name='version_regex'>
	The name of the version_regex to associate with the provided makes.
	</param>

	<example cmd="set firmware make version_regex Mellanox version_regex=mellanox_version">
	Sets the firmware make Mellanox to use the mellanox_version regex when parsing version numbers.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
