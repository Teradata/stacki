# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'software'


	def run(self, args):

		if args and 'software' not in args:
			return

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		pallet_data = self.owner.command('list.pallet', [ 'output-format=json', 'expanded=true' ])
		if pallet_data:
			pallet_data = json.loads(pallet_data)
			pallet_prep = []
			for item in pallet_data:
				boxes = item['boxes'].split()
				#we will set username and password to None to act as a placeholder
				pallet_prep.append({'name':item['name'],
							'version':item['version'],
							'release':item['release'],
							'url':item['url'],
							'urlauthUser':None,
							'urlauthPass':None,
							'boxes':boxes,
							})
		else:
			pallet_prep = []


		cart_data = self.owner.command('list.cart', [ 'expanded=true', 'output-format=json' ])
		if cart_data:
			cart_data = json.loads(cart_data)
			cart_prep = []
			for item in cart_data:
				boxes = item['boxes'].split()
				cart_prep.append({
						'name':item['name'],
						'boxes':boxes,
						'url':item['url'],
						'urlauthUser':None,
						'urlauthPass':None,
						})
		else:
			cart_prep = []

		box_data = self.owner.command('list.box', [ 'output-format=json' ])
		if box_data:
			box_data = json.loads(box_data)
			box_prep = []
			for item in box_data:
				box_prep.append({'name':item['name'], 'os':item['os']})
		else:
			box_prep = []

		document_prep = {}
		document_prep['software'] = {'pallet':pallet_prep,
						'cart':cart_prep,
						'box':box_prep,
						}


		return(document_prep)

