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

class command(stack.commands.add.command):
	pass

class Command(command):
	"""
	Adds a firmware image to stacki.

	<arg type='string' name='version'>
	The firmware version being added. This must be unique within a given firmware family.
	</arg>

	<!-- TODO: update this to work with more than just local files -->
	<param type='string' name='source'>
	The URL pointing to where to retrieve the firmware image. TODO: Currently only supports fetching from local files. Example: file:///export/firmware/my_sweet_image.img
	</param>

	<param type='string' name='family'>
	The firmware family to add this firmware image to. If the family does not already exist, it will be created.
	</param>

	<param type='string' name='make'>
	The optional firmware make to add this firmware image to. If the make does not already exist, it will be created. When make is specified, model is also required.
	</param>

	<param type='string' name='model'>
	The optional firmware model to add this firmware image to. If the model does not already exist, it will be created. When model is specified, make is also required.
	</param>

	<param type='string' name='hash'>
	The optional hash to use when verifying the integrity of the fetched image.
	</param>

	<param type='string' name='hash_alg'>
	The optional hash algorithm to use to verify the integrity of the fetched image. If not specified this defaults to MD5.
	</param>

	<example cmd="add firmware 3.6.5002 source=http://your-sweet-artifactory-builds.labs.teradata.com/firmware/mellanox/img-3.6.5002.img family=mellanox_78xx">
	Fetches the firmware file from the source, associates it with the mellanox_78xx family of firmwares, sets the version to 3.6.5002, and adds it to be tracked in the stacki database.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
