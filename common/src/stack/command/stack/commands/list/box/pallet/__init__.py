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

import stack.commands


class Command(stack.commands.list.box.command):
	"""
	List the pallets enabled in each box.

	<arg optional='1' type='string' name='box' repeat='1'>
	List of boxes.
	</arg>

	<example cmd='list box pallet default'>
	List the pallets used in the "default" box.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		boxes = self.get_box_names(args)

		for box in boxes:
			rows = self.db.select("""
				r.name, r.arch, r.version, r.rel, r.os
				from stacks s, rolls r, boxes b
				where s.roll=r.id and s.box=b.id and b.name=%s
				""", (box,)
			)

			for (roll, arch, version, release, osname) in rows:
				self.addOutput(box, (roll, arch, version, release, osname))

		self.endOutput(
			header=['box', 'pallet', 'arch', 'version', 'release', 'os'],
			trimOwner=False
		)
