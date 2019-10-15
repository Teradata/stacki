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

class Command(stack.commands.list.firmware.command):
	"""
	Lists firmware models tracked by stacki.

	<arg type='string' name='models' repeat='1'>
	Zero or more models to list information for. If no models are specified, all models are listed.
	</arg>

	<param type='string' name='make'>
	The optional make of the models to list. This is required if models are specified as arguments.
	Setting this with no models specified will list all models for the given make.
	</param>

	<param type='bool' name='expanded'>
	Set this to list more detailed firmware model information.
	</param>

	<example cmd="stack list firmware model">
	Lists all firmware models tracked in the stacki database.
	</example>

	<example cmd="stack list firmware model make=mellanox">
	Lists information for all firmware models under the mellanox make.
	</example>

	<example cmd="stack list firmware model m7800 m6036 make=mellanox">
	Lists information for the firmware models m7800 and m6036 under the mellanox make.
	</example>

	<example cmd="stack list firmware model expanded=true">
	Lists additional information for all firmware models tracked in the database.
	</example>
	"""

	def run(self, params, args):
		header = []
		values = []
		for provides, results in self.runPlugins(args = (params, args)):
			header.extend(results["keys"])
			values.extend(results["values"])

		self.beginOutput()
		for owner, vals in values:
			self.addOutput(owner = owner, vals = vals)
		self.endOutput(header = header)
