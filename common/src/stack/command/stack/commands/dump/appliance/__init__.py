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

		self.set_scope('appliance')

		dump = []
		for row in self.call('list.appliance', args):
			name = row['appliance']

			dump.append(OrderedDict(
				name       = name,
				public     = self.str2bool(row['public']),
				attr       = self.dump_attr(name),
				controller = self.dump_controller(name),
				partition  = self.dump_partition(name),
				firewall   = self.dump_firewall(name),
				route      = self.dump_route(name)))

		self.addText(self.dumps(OrderedDict(version   = stack.version,
						    appliance = dump)))
