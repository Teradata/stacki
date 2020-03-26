# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import OrderedDict
import json

import stack
import stack.commands
from stack.commands import EnvironmentArgProcessor

class Command(EnvironmentArgProcessor, stack.commands.dump.command):
	"""
	Dump the contents of the stacki database as json.

	This command dumps specifically the environment level data.
	For each environment, output the name of the environment,
	as well as any environment scoped attributes, storage controller,
	partition, firewall, and route information.

	<example cmd='dump environment'>
	Dump json data for environments in the stacki database
	</example>

	<related>load</related>
	"""

	def run(self, params, args):

		self.set_scope('environment')

		dump = []
		for name in self.getEnvironmentNames():
			dump.append(OrderedDict(
				name          = name,
				attr          = self.dump_attr(name),
				controller    = self.dump_controller(name),
				partition     = self.dump_partition(name),
				firewall      = self.dump_firewall(name),
				route         = self.dump_route(name)))

		self.addText(json.dumps(OrderedDict(version     = stack.version,
						    environment = dump), indent=8))
