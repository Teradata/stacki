# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'global'


	def run(self, args):

		if args and 'global' not in args:
			return

		# if there is no data just return an empty list
		attr_data = self.owner.call('list.attr')
		attr_prep = []
		if attr_data:
			for attr in attr_data:
				if attr['type'] == 'const':
					continue
				else:
					attr_prep.append(attr)

		route_data = self.owner.call('list.route')
		if not route_data:
			route_data = []

		firewall_data = self.owner.call('list.firewall')
		firewall_prep = []
		if firewall_data:
			for rule in firewall_data:
				# if the rule is a const it was created by Stacki, so don't bother dumping it
				if rule['type'] == 'const':
					continue
				if rule['source'] == 'G':
					firewall_prep.append(rule)

		partition_data = self.owner.call('list.storage.partition', [ 'globalOnly=True'] )
		if not partition_data:
			partition_data = []

		controller_data = self.owner.call('list.storage.controller')
		if not controller_data:
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
