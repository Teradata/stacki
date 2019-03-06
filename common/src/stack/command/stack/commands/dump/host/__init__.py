# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import defaultdict
from collections import OrderedDict


class Command(stack.commands.dump.command):

	def run(self, params, args):

		groups = defaultdict(list)
		for row in self.call('list.host.group'):
			if row['groups'] is not None:
				groups[row['host']] = row['groups'].split()

		aliases = defaultdict(lambda: defaultdict(list))
		for row in self.call('list.host.interface.alias'):
			aliases[row['host']][row['interface']].append(row['alias'])

		interfaces = defaultdict(list)
		for row in self.call('list.host.interface'):
			host      = row['host']
			interface = row['interface']
			interfaces[host].append(OrderedDict(
				interface = interface,
				default   = row['default'],
				network   = row['network'],
				mac       = row['mac'],
				ip        = row['ip'],
				name      = row['name'],
				module    = row['module'],
				vlan      = row['vlan'],
				options   = row['options'],
				channel   = row['channel'],
				alias     = aliases[host][interface]))

		self.set_scope('host')

		dump = []
		for row in self.call('list.host', args):
			name = row['host']

			dump.append(OrderedDict(
				name          = name,
				rack          = row['rack'],
				rank          = row['rank'],
				appliance     = row['appliance'],
				box           = row['box'],
				environment   = row['environment'],
				osaction      = row['osaction'],
				installaction = row['installaction'],
				comment       = row['comment'],
				metadata      = self.getHostAttr(name, 
								 'metadata'),
				group         = groups[name],
				interface     = interfaces[name],
				attr          = self.dump_attr(name),
				controller    = self.dump_controller(name),
				partition     = self.dump_partition(name),
				firewall      = self.dump_firewall(name),
				route         = self.dump_route(name)))

		self.addText(self.dumps(OrderedDict(version = stack.version,
						    host    = dump)))

