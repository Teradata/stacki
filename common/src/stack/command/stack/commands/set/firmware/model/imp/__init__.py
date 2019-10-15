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
	Associates a firmware implementation with one or more models.

	<arg type='string' name='models'>
	One or more models to associate the implementation with.
	</arg>

	<param type='string' name='imp'>
	The name of the implementation to associate with the provided models.
	</param>

	<param type='string' name='make'>
	The make of the models.
	</param>

	<example cmd="set firmware model imp m7800 m6036 imp=mellanox_6xxx_7xxx make=mellanox">
	Sets the mellanox_6xxx_7xxx implementation as the one to run for the models m7800 and m6036 for make mellanox.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
