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
	Associates a firmware implementation with one or more makes.

	<arg type='string' name='makes'>
	One or more makes to associate the implementation with.
	</arg>

	<param type='string' name='imp'>
	The name of the implementation to associate with the provided makes.
	</param>

	<example cmd="set firmware make imp Mellanox imp=mellanox_6xxx_7xxx">
	Sets the firmware make Mellanox to run the mellanox_6xxx_7xxx implementation.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
