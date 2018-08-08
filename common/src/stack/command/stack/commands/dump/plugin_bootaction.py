# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'bootaction'


	def run(self, args):
		if args and 'bootaction' not in args:
			return

		document_prep = {'bootaction':[]}

		# if there is no data use an empty list as a placeholder.
		bootaction_data = self.owner.call('list.bootaction')
		if not bootaction_data:
			return document_prep

		bootaction_prep = []
		for item in bootaction_data:
			if item['args']:
				args = item['args'].split()
			else:
				args = []
			bootaction_prep.append({
					'name':item['bootaction'],
					'kernel':item['kernel'],
					'ramdisk':item['ramdisk'],
					'type':item['type'],
					'args':args,
					'os':item['os'],
					})

		document_prep['bootaction'] = bootaction_prep


		return(document_prep)
