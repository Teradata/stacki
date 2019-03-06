# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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
		for row in self.call('list.pallet', ['expanded=true']):
			name    = row['name']
			version = row['version']
			release = row['release']
			arch    = row['arch']
			os      = row['os']

			dump.append(OrderedDict(name    = name,
						version = version,
						release = release,
						arch    = arch,
						os      = os))

		self.addText(self.dumps(OrderedDict(version  = stack.version,
						    software = {'pallet' : dump})))

