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

class command(stack.commands.add.command, FirmwareArgumentProcessor):
	pass

class Command(command):
	"""
	Adds a firmware image to stacki.

	<arg type='string' name='version'>
	The firmware version being added. This must be unique for make + model.
	</arg>

	<param type='string' name='source'>
	The URL pointing to where to retrieve the firmware image.
	</param>

	<param type='string' name='make'>
	The firmware make to add this firmware image to. If the make does not already exist, it will be created.
	</param>

	<param type='string' name='model'>
	The firmware model to add this firmware image to. If the model does not already exist, it will be created.
	</param>

	<param type='string' name='hash'>
	The optional hash to use when verifying the integrity of the fetched image.
	</param>

	<param type='string' name='hash_alg'>
	The optional hash algorithm to use to verify the integrity of the fetched image. If not specified this defaults to MD5.
	</param>

	<example cmd="add firmware 3.6.5002 source=file:///export/some/path/img-3.6.5002.img make=Mellanox model=7800">
	Fetches the firmware file from the source (a local file on the front end in /export/some/path), associates it with the
	Mellanox make and 7800 model, sets the version to 3.6.5002, and adds it to be tracked in the stacki database.
	</example>

	<example cmd="add firmware 3.6.5002 source=http://www.your-sweet-site.com/firmware/mellanox/img-3.6.5002.img make=Mellanox model=7800">
	This performs the same steps as the previous example except the image is fetched via HTTP.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
