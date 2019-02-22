# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict
import json


class Command(stack.commands.dump.command):

	def run(self, params, args):

		self.set_scope('software')

		dump = []
		for row in self.call('list.cart'):
			dump.append(OrderedDict(name = row['name']))

		self.addText(json.dumps(OrderedDict(version  = stack.version,
						    software = {'cart' : dump}),
					indent=8))

