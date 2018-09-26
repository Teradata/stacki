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
from stack.commands.argument_processors import FirmwareArgumentProcessor

class command(stack.commands.remove.command, FirmwareArgumentProcessor):
	pass

class Command(command):
	"""
	Removes firmware images from stacki.

	<arg type='string' name='version' repeat='1'>
	One or more firmware versions to be removed.
	</arg>

	<param type='string' name='make'>
	The firmware make to remove this firmware image from.
	</param>

	<param type='string' name='model'>
	The firmware model to remove this firmware image from.
	</param>

	<example cmd="remove firmware 3.6.5002 make=mellanox model=7800">
	Removes the firmware with version 3.6.5002 for the mellanox 7800 make and model.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
