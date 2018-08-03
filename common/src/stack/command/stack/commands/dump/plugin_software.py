# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'software'


	def run(self, args):

		if args and 'software' not in args:
			return

		# if there is no data return an empty list
		pallet_data = self.owner.call('list.pallet', [ 'expanded=true' ])
		pallet_prep = []
		if pallet_data:
			for item in pallet_data:
				boxes = item['boxes'].split()
				# set username and password to None to act as a placeholder
				pallet_prep.append({'name':item['name'],
							'version':item['version'],
							'release':item['release'],
							'url':item['url'],
							'urlauthUser':None,
							'urlauthPass':None,
							'boxes':boxes,
							})

		cart_data = self.owner.call('list.cart', [ 'expanded=true' ])
		cart_prep = []
		if cart_data:
			for item in cart_data:
				boxes = item['boxes'].split()
				cart_prep.append({
						'name':item['name'],
						'boxes':boxes,
						'url':item['url'],
						'urlauthUser':None,
						'urlauthPass':None,
						})

		box_data = self.owner.call('list.box')
		box_prep = []
		if box_data:
			for item in box_data:
				box_prep.append({'name':item['name'], 'os':item['os']})

		document_prep = {}
		document_prep['software'] = {'pallet':pallet_prep,
						'cart':cart_prep,
						'box':box_prep,
						}


		return(document_prep)
