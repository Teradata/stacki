# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict


class Command(stack.commands.dump.command):

	def run(self, params, args):

		self.set_scope('software')

		dump = []
		for row in self.call('list.cart'):
			dump.append(OrderedDict(name = row['name']))

		self.addText(self.dumps(OrderedDict(version  = stack.version,
						    software = {'cart' : dump})))

