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

