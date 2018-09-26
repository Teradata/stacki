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
	Disassociates firmware version_regexes from one or more models.

	<arg type='string' name='models'>
	One or more models to disassociate from a version_regex.
	</arg>

	<param type='string' name='make'>
	The make of the provided models.
	</param>

	<example cmd="remove firmware model version_regex m7800 m6036 make=Mellanox">
	Disassociates the m7800 and m6036 models for the Mellanox make from any version_regexes that were set for them.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
