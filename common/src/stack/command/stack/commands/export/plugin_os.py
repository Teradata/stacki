# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'os'


	def run(self, args):

		if args:
			if 'os' not in args:
				return

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		os_data = self.owner.command('list.os', [ 'output-format=json' ])
		document_prep = {'os':[]}
		if os_data:
			os_data = json.loads(os_data)
			for item in os_data:
				os_name = item['os']

				attr_data = self.owner.command('list.os.attr', [ f'os={os_name}', 'output-format=json' ])
				if attr_data:
					attr_data = json.loads(attr_data)
				else:
					attr_data = []
				attr_prep = []
				for item in attr_data:
					if item['os'] == os_name:
						attr_prep.append(item)

				route_data = self.owner.command('list.os.route', [ f'os={os_name}', 'output-format=json' ])
				if route_data:
					route_data = json.loads(route_data)
				else:
					route_data = []

				firewall_data = self.owner.command('list.os.firewall', [ f'os={os_name}', 'output-format=json' ])
				if firewall_data:
					firewall_data = json.loads(firewall_data)
					firewall_prep = []
					for item in firewall_data:
						if item['os'] == os_name and item['source'] == 'O':
							firewall_prep.append(item)
				else:
					firewall_prep = []

				partition_data = self.owner.command('list.storage.partition', [ f'{os_name}', 'globalOnly=False', 'output-format=json' ])
				if partition_data:
					partition_data = json.loads(partition_data)
				else:
					partition_data = []

				controller_data = self.owner.command('list.storage.controller', [ f'{os_name}', 'output-format=json' ])
				if controller_data:
					controller_data = json.loads(controller_data)
				else:
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

