# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'environment'


	def run(self, args):

		if args:
			if 'environment' not in args:
				return

		document_prep = {'environment':[]}

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		environment_data = self.owner.command('list.environment', [ 'output-format=json' ])
		if environment_data:
			environment_data = json.loads(environment_data)
			for item in environment_data:
				environment_name = item['environment']

				attr_data = self.owner.command('list.environment.attr', [ f'{environment_name}', 'output-format=json' ])
				if attr_data:
					attr_data = json.loads(attr_data)
				else:
					attr_data = []

				route_data = self.owner.command('list.route', [ f'environment={environment_name}', 'output-format=json' ])
				if route_data:
					route_data = json.loads(route_data)
				else:
					route_data = []

				firewall_data = self.owner.command('list.firewall', [ f'environment={environment_name}', 'output-format=json' ])
				if firewall_data:
					firewall_data = json.loads(firewall_data)
				else:
					firewall_data = []

				partition_data = self.owner.command('list.storage.partition', [ f'environment={environment_name}', 'globalOnly=False', 'output-format=json' ])
				if partition_data:
					partition_data = json.loads(partition_data)
				else:
					partition_data = []

				controller_data = self.owner.command('list.storage.controller', [ f'environment={environment_name}', 'output-format=json' ])
				if controller_data:
					controller_data = json.loads(controller_data)
				else:
					controller_data = []
				controller_prep = []
				for item in controller_data:
					options = item['options'].split()
					controller_prep.append({'scope':item['scope'], 'enclosure':item['enclosure'], 'adapter':item['adapter'], 'slot':item['slot'],
								'raidlevel':item['raidlevel'], 'arrayid':item['arrayid'], 'options':options})


				document_prep['environment'].append({'name':environment_name, 'attrs':attr_data, 'route':route_data, 'firewall':firewall_data, 'partition':partition_data, 'controller':controller_prep})


		return(document_prep)

