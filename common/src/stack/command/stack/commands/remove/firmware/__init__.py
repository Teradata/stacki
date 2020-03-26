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
from stack.commands import FirmwareArgProcessor

class command(stack.commands.remove.command, FirmwareArgProcessor):
	pass

class Command(command):
	"""
	Removes firmware images from stacki.

	<arg type='string' name='version' repeat='1'>
	Zero or more firmware versions to be removed. If no versions are specified, all will be removed.
	If one or more versions are specified, the make and model parameters are required.
	</arg>

	<param type='string' name='make'>
	The optional make of the firmware to remove.
	If this is specified but no versions or model are specified, this will remove all firmware versions for the make.
	</param>

	<param type='string' name='model'>
	The optional model of the firmware to remove.
	If this is specified, make is required.
	If no versions are specified but make and model are specified, all firmware versions for that make and model will be removed.
	</param>

	<example cmd="remove firmware">
	Removes all firmware.
	</example>

	<example cmd="remove firmware 3.6.5002 make=mellanox model=m7800">
	Removes the firmware with version 3.6.5002 for the mellanox m7800 make and model.
	</example>

	<example cmd="remove firmware make=mellanox">
	Removes all firmware for the mellanox make.
	</example>

	<example cmd="remove firmware make=mellanox model=m7800">
	Removes all firmware for the mellanox make and m7800 model.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
