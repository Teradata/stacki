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
	Adds a firmware version regex to the stacki database

	<arg type='string' name='regex'>
	A valid Python regex to use to use against the version number returned from the target hardware.
	</arg>

	<param type='string' name='name'>
	The human readable name for this regex.
	</param>

	<example cmd="add firmware version_regex '(?:\d+\.){2}\d+' name=Mellanox">
	Adds a regex with the name Mellanox that looks for three number groups separated by dots to the Stacki database. This turns "X86_64 3.6.5009 2018-01-02 07:42:21 x86_64" into "3.6.5009".
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
