# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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

class Command(stack.commands.add.firmware.command):
	"""
	Adds a firmware implementation to the stacki database

	<arg type='string' name='name'>
	The name of the implementation file to run, without the "imp_" prepended or the extension appended.
	</arg>

	<param type='string' name='make'>
	The optional make that this implementation applies to.
	</param>

	<param type='string' name='models'>
	The optional models for the given make that this implementation applies to. Multiple models should be specified as a comma separated list.
	If this is specified, make is also required.
	</param>

	<example cmd="add firmware imp mellanox_6xxx_7xxx make=Mellanox models=m6036,m7800">
	Marks the firmware implementation named mellanox_6xxx_7xxx as the one to run for Mellanox m6036 and m7800 devices.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
