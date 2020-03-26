# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import OrderedDict
import json

import stack
import stack.commands
from stack.commands import OSArgProcessor

class Command(OSArgProcessor, stack.commands.dump.command):
	"""
	Dump the contents of the stacki database as json.

	This command dumps specifically the OS level data.
	For each OS, output the name of the OS, as well as
	any OS scoped attributes, storage controller,
	partition, firewall, and route information.

	<example cmd='dump os'>
	Dump json data for OSes in the stacki database
	</example>

	<related>load</related>
	"""

	def run(self, params, args):

		self.set_scope('os')

		dump = []
		for name in self.getOSNames():
			dump.append(OrderedDict(
				name          = name,
				attr          = self.dump_attr(name),
				controller    = self.dump_controller(name),
				partition     = self.dump_partition(name),
				firewall      = self.dump_firewall(name),
				route         = self.dump_route(name)))

		self.addText(json.dumps(OrderedDict(version  = stack.version,
						    os       = dump), indent=8))
