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


class Command(stack.commands.add.host.command):
	"""
	Adds a firmware image to the correct directory structure for list firmware and sync firmware to pick it up.

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
		host, = self.getHostnames(args)

		(imagepath, ) = self.fillParams([
			('imagepath',    False),
		])

		# Make sure empty strings are converted to None
		(imagepath, ) = map(blank_str_to_None, ( imagepath,))

		# Gotta have an image
		if not imagepath:
			raise ParamRequired(self, ('imagepath'))

		base = '/export/stack/firmware/'
		info = self.getHostAttrDict(host)
		appliance = info.get(host).get('appliance')
		make = info.get(host).get('component.make')
		model = info.get(host).get('component.model')

		if not make or make=='None':
			make = ""
		if not model or model=='None':
			model = ""

		filename = os.path.basename(imagepath)
		destination = os.path.join(base, appliance, make, model)

		if not os.path.isfile(imagepath):
			raise ParamValue(self, 'imagepath', 'valid path to firmware image')

		if not os.path.exists(destination):
			os.makedirs(destination)

		shutil.move(imagepath, destination)	#Can replace move to copy2
