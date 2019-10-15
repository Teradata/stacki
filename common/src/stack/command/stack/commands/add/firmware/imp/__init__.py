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

class Command(stack.commands.add.firmware.command):
	"""
	Adds a firmware implementation to the stacki database.

	<arg type='string' name='name'>
	The name of the implementation file to run, without the "imp_" prepended or the extension appended.
	</arg>

	<param type='string' name='models'>
	Zero or more models that this implementation applies to. Multiple models should be specified as a comma separated list.
	If this is specified, make is also required.
	</param>

	<param type='string' name='make'>
	The optional make of the models this implementation applies to. If this is specified, models are also required.
	</param>

	<example cmd="add firmware imp mellanox_6xxx_7xxx make=mellanox model='m7800, m6036'">
	Adds the firmware implementation named mellanox_6xxx_7xxx and sets it to be the one run for make mellanox and models m7800 and m6036.
	</example>

	<example cmd="add firmware imp mellanox_6xxx_7xxx">
	This simply adds the implementation named mellanox_6xxx_7xxx to be tracked by stacki.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
