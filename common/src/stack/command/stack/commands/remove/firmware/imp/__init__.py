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
	Removes firmware implementations from the stacki database.

	<arg type='string' name='imps'>
	One or more implementations to remove.
	</arg>

	<example cmd="remove firmware imp mellanox_m6xxx_7xxx intel_special">
	Removes the mellanox_m6xxx_7xxx and intel_special implementations from the database.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
