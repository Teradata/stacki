# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'environment'


	def run(self, args):

		if args and 'environment' not in args:
			return

		document_prep = {'environment':[]}

		# if there is no data, just return an empty list
		environment_data = self.owner.call('list.environment')
		if not environment_data:
			return document_prep

		for item in environment_data:
			environment_name = item['environment']

			attr_data = self.owner.call('list.environment.attr', [ environment_name ])
			if not attr_data:
				attr_data = []

			route_data = self.owner.call('list.route', [ f'environment={environment_name}' ])
			if not route_data:
				route_data = []

			firewall_data = self.owner.call('list.firewall', [ f'environment={environment_name}' ])
			if not firewall_data:
				firewall_data = []

			partition_data = self.owner.call('list.storage.partition', [ f'environment={environment_name}', 'globalOnly=False' ])
			if not partition_data:
				partition_data = []

			controller_data = self.owner.call('list.storage.controller', [ f'environment={environment_name}' ])
			if not controller_data:
				controller_data = []

			controller_prep = []
			for item in controller_data:
				options = item['options'].split()
				controller_prep.append({
						'scope':item['scope'],
						'enclosure':item['enclosure'],
						'adapter':item['adapter'],
						'slot':item['slot'],
						'raidlevel':item['raidlevel'],
						'arrayid':item['arrayid'],
						'options':options,
						})


			document_prep['environment'].append({
							'name':environment_name,
							'attrs':attr_data,
							'route':route_data,
							'firewall':firewall_data,
							'partition':partition_data,
							'controller':controller_prep,
							})


		return(document_prep)
