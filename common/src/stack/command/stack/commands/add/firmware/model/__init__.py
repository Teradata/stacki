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
	Adds a firmware model to the stacki database.

	<arg type='string' name='model' repeat='1'>
	One or more model names to add. model names are required to be unique, and any duplicates will be ignored.
	</arg>

	<param type='string' name='make'>
	The maker of the models being added. If this does not correspond to an already existing make, one will be added.
	</param>

	<example cmd="add firmware model awesome_9001 mediocre_5200 make='boss hardware corp'">
	Adds two models with the names 'awesome_9001' and 'mediocre_5200' to the set of available firmware models under the 'boss hardware corp' make.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
