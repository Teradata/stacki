# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

from collections import defaultdict

import stack.commands
from stack.argument_processors.box import BoxArgProcessor
from stack.argument_processors.repo import RepoArgProcessor

class command(BoxArgProcessor, RepoArgProcessor, stack.commands.list.command):
	pass


class Command(command):
	"""
	Lists the pallets and carts that are associated with boxes.

	<arg optional='1' type='string' name='box' repeat='1'>
	Optional list of box names.
	</arg>

	<example cmd='list box'>
	List all known box definitions.
	</example>
	"""

	def run(self, params, args):
		pallets = {}
		carts	= {}
		repos	= defaultdict(list)

		for box in self.get_box_names(args):
			for pallet in self.get_box_pallets(box):
				fullname = '%s-%s' % (pallet.name, pallet.version)
				if pallet.rel:
					fullname += '-%s' % pallet.rel

				if box not in pallets:
					pallets[box] = []
				pallets[box].append(fullname)

		for row in self.call('list.cart'):
			if row['boxes']:
				for box in row['boxes'].split():
					if box not in carts:
						carts[box] = []
					carts[box].append(row['name'])

		for box in self.get_box_names(args):
			for repo_data in self.get_repos_by_box(box).values():
				for repo in repo_data.values():
					repos[box].append(repo['alias'])

		self.beginOutput()

		for box in self.get_box_names(args):
			id, os = self.db.select("""
				b.id, o.name from boxes b, oses o
				where b.name=%s	and b.os=o.id
				""", (box,)
			)[0]

			if box not in carts:
				carts[box] = []

			if box not in pallets:
				pallets[box] = []

			self.addOutput(box, (
				os, ' '.join(pallets[box]), ' '.join(carts[box]), ' '.join(repos[box]),
			))

		self.endOutput(
			header=['name', 'os', 'pallets', 'carts', 'repos'],
			trimOwner=False
		)
