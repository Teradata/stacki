# @copyright@
# @copyright@

import os
import stack.commands


class Implementation(stack.commands.Implementation):

	def run(self, args):
		host	= args[0]
		server	= args[1]
		box	= self.owner.getHostAttr(host, 'box')
		repo	= []

		repo.append('<stack:file stack:name="/etc/apt/sources.list.d/stacki.list">')

		for pallet in self.owner.get_box_pallets(box):
			rel_path = f'pallets/{pallet.name}/{pallet.version}/{pallet.rel}/{pallet.os}/{pallet.arch}/packages'

			if os.path.exists(os.path.join('/export/stack', rel_path)):
				repo.append(f'deb [trusted=yes] http://{server}/install/{rel_path}/packages ./')

		repo.append('</stack:file>')


		for line in repo:
			self.owner.addOutput(host, line)


