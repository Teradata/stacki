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
	Disassociates firmware implementations from one or more makes.

	<arg type='string' name='makes'>
	One or more makes to disassociate from an implementation.
	</arg>

	<example cmd="remove firmware make imp Mellanox Intel">
	Disassociates the Mellanox and Intel makes from any custom implementations that were set for them.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
