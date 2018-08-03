# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'os'


	def run(self, args):

		if args and 'os' not in args:
			return

		# if there is no data return an empty list
		os_data = self.owner.call('list.os')
		document_prep = {'os':[]}
		if not os_data:
			return document_prep

		for item in os_data:
			os_name = item['os']

			attr_data = self.owner.call('list.os.attr', [ f'os={os_name}' ])
			if not attr_data:
				attr_data = []
			attr_prep = []
			for item in attr_data:
				if item['os'] == os_name:
					attr_prep.append(item)

			route_data = self.owner.call('list.os.route', [ f'os={os_name}' ])
			if not route_data:
				route_data = []

			firewall_data = self.owner.call('list.os.firewall', [ f'os={os_name}' ])
			if not firewall_data:
				firewall_data = []
			firewall_prep = []
			for item in firewall_data:
				if item['os'] == os_name and item['source'] == 'O':
					firewall_prep.append(item)

			partition_data = self.owner.call('list.storage.partition', [ f'{os_name}', 'globalOnly=False' ])
			if not partition_data:
				partition_data = []

			controller_data = self.owner.call('list.storage.controller', [ f'{os_name}' ])
			if not controller_data:
				controller_data = []

			controller_prep = []
			for item in controller_data:
				options = item['options'].split()
				controller_prep.append({'scope':item['scope'],
							'enclosure':item['enclosure'],
							'adapter':item['adapter'],
							'slot':item['slot'],
							'raidlevel':item['raidlevel'],
							'arrayid':item['arrayid'],
							'options':options,
							})


			document_prep['os'].append({'name':os_name,
							'attrs':attr_prep,
							'route':route_data,
							'firewall':firewall_prep,
							'partition':partition_data,
							'controller':controller_prep,
							})


		return(document_prep)
