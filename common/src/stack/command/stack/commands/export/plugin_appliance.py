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
		if args:
			if 'appliance' not in args:
				return

		document_prep = {'appliance':[]}

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		appliance_data = self.owner.command('list.appliance', [ 'output-format=json' ])
		if appliance_data:
			appliance_data = json.loads(appliance_data)

			for item in appliance_data:
				appliance_name = item['appliance']

				attr_data = self.owner.command('list.appliance.attr', [ f'{appliance_name}', 'output-format=json' ])
				if attr_data:
					attr_data = json.loads(attr_data)
				else:
					attr_data = []

				route_data = self.owner.command('list.appliance.route', [ f'{appliance_name}', 'output-format=json' ])
				if route_data:
					route_data = json.loads(route_data)
				else:
					route_data = []

				firewall_data = self.owner.command('list.appliance.firewall', [ f'{appliance_name}', 'output-format=json' ])
				firewall_prep = []
				if firewall_data:
					firewall_data = json.loads(firewall_data)
					for rule in firewall_data:
						if rule['source'] == 'A':
							firewall_prep.append(rule)

				partition_data = self.owner.command('list.storage.partition', [ f'{appliance_name}', 'globalOnly=False', 'output-format=json' ])
				if partition_data:
					partition_data = json.loads(partition_data)
				else:
					partition_data = []

				controller_data = self.owner.command('list.storage.controller', [ f'{appliance_name}', 'output-format=json' ])
				if controller_data:
					controller_data = json.loads(controller_data)
				else:
					controller_data = []

				document_prep['appliance'].append({'name':appliance_name,
									'longname':item['long name'],
									'attrs':attr_data,
									'route':route_data,
									'firewall':firewall_prep,
									'partition':partition_data,
									'controller':controller_data})


		return(document_prep)

