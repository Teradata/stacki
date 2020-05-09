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
			for pal in self.get_box_pallets(box):
				self.addOutput(box, (pal.name, pal.arch, pal.version, pal.rel, pal.os))

		self.endOutput(
			header=['box', 'pallet', 'arch', 'version', 'release', 'os'],
			trimOwner=False
		)
