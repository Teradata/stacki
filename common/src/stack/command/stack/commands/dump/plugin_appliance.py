# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'appliance'


	def run(self, args):
		if args and 'appliance' not in args:
			return

		document_prep = {'appliance':[]}

		# if there is no data use an empty list as a placeholder.
		appliance_data = self.owner.call('list.appliance')
		if not appliance_data:
			return document_prep

		for item in appliance_data:
			appliance_name = item['appliance']

			attr_data = self.owner.call('list.appliance.attr', [ appliance_name ])
			if not attr_data:
				attr_data = []

			route_data = self.owner.call('list.appliance.route', [ appliance_name ])
			if not route_data:
				route_data = []

			firewall_data = self.owner.call('list.appliance.firewall', [ appliance_name ])
			firewall_prep = []
			if firewall_data:
				for rule in firewall_data:
					if rule['source'] == 'A':
						firewall_prep.append(rule)

			partition_data = self.owner.call('list.storage.partition', [ appliance_name, 'globalOnly=False'])
			if not partition_data:
				partition_data = []

			controller_data = self.owner.call('list.storage.controller', [ appliance_name ])
			if not controller_data:
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
