# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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

class Command(stack.commands.list.host.firmware.command):
	"""
	Lists the firmware mappings that exist in the stacki database.

	<arg type='string' name='host' repeat='1'>
	Zero or more hostnames to filter the results by.
	</arg>

	<param type='string' name='versions'>
	Zero or more firmware versions to filter by. Multiple versions should be specified as a comma separated list.
	If one or more versions are specified, the make and model parameters are required.
	</param>

	<param type='string' name='make'>
	The optional make of the firmware to filter by.
	</param>

	<param type='string' name='model'>
	The optional model of the firmware to filter by.
	If this is specified, make is required.
	</param>

	<param type='string' name='sort'>
	The value to sort the results by. Should be one of 'host', 'make', 'model', or 'version'.
	</param>

	<example cmd="stack list host firmware mapping">
	Lists all of the firmware mappings for all hosts.
	</example>

	<example cmd="stack list host firmware mapping switch-13-11">
	Lists all of the firmware mappings for the host named switch-13-11.
	</example>

	<example cmd="stack list host firmware mapping switch-13-11 switch-13-12 versions=3.6.5002,3.6.8010 make=mellanox model=m7800">
	Lists all of the firmware mappings for firmware versions 3.6.5002 and 3.6.8010 for make mellanox and model m7800 that are
	mapped to the hosts named switch-13-11 and switch-13-12.
	</example>

	<example cmd="stack list host firmware mapping versions=3.6.5002,3.6.8010 make=mellanox model=m7800">
	Lists all of the firmware mappings for firmware versions 3.6.5002 and 3.6.8010 for make mellanox and model m7800 for all hosts.
	</example>

	<example cmd="stack list host firmware mapping a:switch make=mellanox model=m7800">
	Lists all of the firmware mappings for make mellanox and model m7800 for all hosts that are switch appliances.
	</example>

	<example cmd="stack list host firmware mapping make=mellanox model=m7800">
	Lists all of the firmware mappings for make mellanox and model m7800 for all hosts.
	</example>

	<example cmd="stack list host firmware mapping switch-13-11 make=mellanox">
	Lists all of the firmware mappings for make mellanox for the host with the name switch-13-11.
	</example>

	<example cmd="stack list host firmware mapping make=mellanox">
	Lists all of the firmware mappings for make mellanox for all hosts.
	</example>
	"""

	def run(self, params, args):
		header = []
		values = []
		for provides, results in self.runPlugins(args = (params, args)):
			header.extend(results['keys'])
			values.extend(results['values'])

		self.beginOutput()
		for owner, vals in values:
			self.addOutput(owner = owner, vals = vals)
		self.endOutput(header = header)
