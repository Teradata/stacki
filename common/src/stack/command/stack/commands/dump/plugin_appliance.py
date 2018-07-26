# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'appliance'


	def run(self, args):
		if args and 'appliance' not in args:
			return

		document_prep = {'appliance':[]}

		# json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		# if not, use an empty list as a placeholder.
		appliance_data = self.owner.call('list.appliance')
		if not appliance_data:
			return document_prep

		appliance_data = json.loads(appliance_data)

		for item in appliance_data:
			appliance_name = item['appliance']

			attr_data = self.owner.call('list.appliance.attr', [ appliance_name ])
			if attr_data:
				attr_data = json.loads(attr_data)
			else:
				attr_data = []

			route_data = self.owner.call('list.appliance.route', [ appliance_name ])
			if route_data:
				route_data = json.loads(route_data)
			else:
				route_data = []

			firewall_data = self.owner.call('list.appliance.firewall', [ appliance_name ])
			firewall_prep = []
			if firewall_data:
				firewall_data = json.loads(firewall_data)
				for rule in firewall_data:
					if rule['source'] == 'A':
						firewall_prep.append(rule)

			partition_data = self.owner.call('list.storage.partition', [ appliance_name, 'globalOnly=False'])
			if partition_data:
				partition_data = json.loads(partition_data)
			else:
				partition_data = []

			controller_data = self.owner.call('list.storage.controller', [ appliance_name ])
			if controller_data:
				controller_data = json.loads(controller_data)
			else:
				controller_data = []

			document_prep['appliance'].append({
							'name':appliance_name,
							'longname':item['long name'],
							'attrs':attr_data,
							'route':route_data,
							'firewall':firewall_prep,
							'partition':partition_data,
							'controller':controller_data
							})
		return(document_prep)

