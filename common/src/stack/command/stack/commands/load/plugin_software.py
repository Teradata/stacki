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

	def load_pallet(self, pallets):
		for p in pallets:
			pallet = p.get('name')
			params = {'version': p.get('version'),
				  'release': p.get('release'),
				  'arch':    p.get('arch'),
				  'os':      p.get('os')}
			for t in p.get('tag', []):
				params['tag']   = t.get('name')
				params['value'] = t.get('value')
				self.owner.stack('add.pallet.tag', pallet, **params)

			
	def load_box(self, boxes):
		for b in boxes:
			box    = b.get('name')
			params = {'os': b.get('os')}

			self.owner.stack('add.box', box, **params)

			for p in b.get('pallet', []):
				pallet = p.get('name')
				params = {'box'    : box,
					  'version': p.get('version'),
					  'release': p.get('release'),
					  'arch'   : p.get('arch'),
					  'os'     : p.get('os')}

				self.owner.stack('enable.pallet', pallet, **params)

			for c in b.get('cart', []):
				cart   = c.get('name')
				params = {'box': box}

				self.owner.stack('enable.cart', cart, **params)



	def run(self, section):
		self.load_box(section.get('box', []))
		self.load_pallet(section.get('pallet', []))
