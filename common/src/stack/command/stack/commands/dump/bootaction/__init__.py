# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict
import json


class Command(stack.commands.dump.command):
	"""
	Dump the contents of the stacki database as json.

	This command dumps specifically the bootaction data.
	For each bootaction, output the name, type, OS, kernel,
	ramdisk, and kernel boot args.

	<example cmd='dump bootaction'>
	Dump json data for bootactions in the stacki database
	</example>

	<related>load</related>
	"""

	def run(self, params, args):
		dump = []

		for row in self.call('list.bootaction'):
			dump.append(OrderedDict(
				name    = row['bootaction'],
				type    = row['type'],
				os      = row['os'],
				kernel  = row['kernel'],
				ramdisk = row['ramdisk'],
				args    = row['args']))

		self.addText(json.dumps(OrderedDict(version    = stack.version,
						    bootaction = dump), indent=8))
