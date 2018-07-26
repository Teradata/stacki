# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'global'


	def run(self, args):

		if args and 'global' not in args:
			return

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		attr_data = self.owner.command('list.attr', [ 'output-format=json' ])
		attr_prep = []
		if attr_data:
			attr_data = json.loads(attr_data)
			for attr in attr_data:
				if attr['type'] == 'const':
					continue
				else:
					attr_prep.append(attr)

		route_data = self.owner.command('list.route', [ 'output-format=json' ])
		if route_data:
			route_data = json.loads(route_data)
		else:
			route_data = []

		firewall_data = self.owner.command('list.firewall', [ 'output-format=json' ])
		firewall_prep = []
		if firewall_data:
			firewall_data = json.loads(firewall_data)
			for rule in firewall_data:
				# if the rule is a const, we do not need to bother dumping it
				if rule['type'] == 'const':
					continue
				if rule['source'] == 'G':
					firewall_prep.append(rule)

		partition_data = self.owner.command('list.storage.partition', [ 'globalOnly=True', 'output-format=json' ])
		if partition_data:
			partition_data = json.loads(partition_data)
		else:
			partition_data = []

		controller_data = self.owner.command('list.storage.controller', [ 'output-format=json' ])
		if controller_data:
			controller_data = json.loads(controller_data)
		else:
			controller_data = []

		document_prep = {}
		document_prep['global'] = {
					'attrs':attr_prep,
					'route':route_data,
					'firewall':firewall_prep,
					'partition':partition_data,
					'controller':controller_data,
					}

		return(document_prep)


