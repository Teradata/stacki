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
from stack.commands import FirmwareArgProcessor, HostArgProcessor

class command(stack.commands.add.command, FirmwareArgProcessor):
	pass

class Command(command, HostArgProcessor):
	"""
	Adds a firmware image to stacki.

	<arg type='string' name='version'>
	The firmware version being added. This must be unique for make + model.
	</arg>

	<param type='string' name='source'>
	The URL or local file path pointing to where to retrieve the firmware image.
	</param>

	<param type='string' name='make'>
	The firmware make to add this firmware image to. If the make does not already exist, it will be created.
	</param>

	<param type='string' name='model'>
	The firmware model to add this firmware image to. If the model does not already exist, it will be created.
	</param>

	<param type='string' name='imp'>
	The optional firmware implementation to run for the model this firmware is for. If the make + model provided does not already
	exist, this parameter is required. If the implementation does not already exist, it will be created.
	</param>

	<param type='string' name='hosts'>
	The optional host names to associate with this firmware. This can either be a single host name, a comma separate list of hosts,
	or one of the common host name specifiers like 'a:switch'.
	</param>

	<param type='string' name='hash'>
	The optional hash to use when verifying the integrity of the fetched image.
	</param>

	<param type='string' name='hash_alg'>
	The optional hash algorithm to use to verify the integrity of the fetched image. If not specified this defaults to MD5.
	</param>

	<example cmd="add firmware 3.6.5002 source=/export/some/path/img-3.6.5002.img make=Mellanox model=m7800 imp=mellanox_m7800">
	Fetches the firmware file from the source (a local file on the front end in /export/some/path), associates it with the
	Mellanox make and 7800 model, and sets the version to 3.6.5002, and adds it to be tracked in the stacki database.
	</example>

	<example cmd="add firmware 3.6.5002 source=http://www.your-sweet-site.com/firmware/mellanox/img-3.6.5002.img make=Mellanox model=m7800 imp=mellanox_m7800">
	This performs the same steps as the previous example except the image is fetched via HTTP.
	</example>

	<example cmd="add firmware 3.6.5002 source=http://www.your-sweet-site.com/firmware/mellanox/img-3.6.5002.img make=Mellanox model=m7800 hosts=switch-0-1,switch-0-2">
	This performs the same steps as the previous example except the firmware gets associated with the hosts named switch-0-1 and switch-0-2.
	</example>

	<example cmd="add firmware 3.6.5002 source=http://www.your-sweet-site.com/firmware/mellanox/img-3.6.5002.img make=Mellanox model=m7800 hosts=a:switch">
	This performs the same steps as the previous example except the firmware gets associated with all hosts that are of the appliance switch type.
	</example>

	<example cmd="add firmware 1.2.3.4 source=/export/some/path/my-file make=new_make model=new_model imp=new_imp">
	Assuming that the make, model, and implementation do no already exist, this adds a new firmware version 1.2.3.4
	associated with new_make and new_model that will use new_imp to read and write to mapped hosts.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
