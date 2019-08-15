# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'software'

	def requires(self):
		return ['os']

	def run(self, section):

		try:
			boxes = section['box']
		except KeyError:
			boxes = []
		for b in boxes:
			box    = b.get('name')
			params = {'os': b.get('os')}

			self.owner.stack('add.box', box, **params)

			try:
				pallets = b['pallet']
			except KeyError:
				pallets = []
			for p in pallets:
				pallet = p.get('name')
				params = {'box'    : box,
					  'version': p.get('version'),
					  'release': p.get('release'),
					  'arch'   : p.get('arch'),
					  'os'     : p.get('os')}

				self.owner.stack('enable.pallet', pallet, **params)

			try:
				carts = b['cart']
			except KeyError:
				carts = []
			for c in carts:
				cart   = c.get('name')
				params = {'box': box}

				self.owner.stack('enable.cart', cart, **params)




