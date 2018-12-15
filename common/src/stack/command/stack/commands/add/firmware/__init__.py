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
from stack.exception import ParamRequired, ArgUnique, CommandError, ParamValue
from stack.util import blank_str_to_None
import os
import shutil

class command(stack.commands.add.command):
	pass

class Command(command):
	"""
	TODO - add actual docstring
	Adds a firmware image to stacki.

	<arg type='string' name='host'>
	Host name of machine
	</arg>

	<param type='string' name='imagepath'>
	The image that needs to be put in the correct folder structure
	</param>

	<example cmd="add host firmware infiniband-10-12 imagepath='/foo/bar/firm.img'">
	MOVES the firmware image from foo/bar/firm.img to the appropriate directory structure for list and sync firmware commands. Directory Structure: /export/stack/firmware/appliance/make/model
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
