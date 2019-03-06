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

		dump = []
		for row in self.call('list.network'):
			dump.append(OrderedDict(
				name    = row['network'],
				address = row['address'],
				mask    = row['mask'],
				gateway = row['gateway'],
				mtu     = row['mtu'],
				zone    = row['zone'],
				dns     = self.str2bool(row['dns']),
				pxe     = self.str2bool(row['pxe'])))

		self.addText(self.dumps(OrderedDict(version = stack.version,
						    network = dump)))

