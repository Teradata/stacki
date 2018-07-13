# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'bootaction'


	def run(self, args):
		if args:
			if 'bootaction' not in args:
				return

		document_prep = {'bootaction':[]}

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		bootaction_data = self.owner.command('list.bootaction', [ 'output-format=json' ])
		if bootaction_data:
			bootaction_data = json.loads(bootaction_data)

			bootaction_prep = []
			for item in bootaction_data:
				if item['args']:
					args = item['args'].split()
				else:
					args = []
				bootaction_prep.append({'name':item['bootaction'],
									'kernel':item['kernel'],
									'ramdisk':item['ramdisk'],
									'type':item['type'],
									'args':args,
									'os':item['os'],
									})

			document_prep['bootaction'] = bootaction_prep


		return(document_prep)

