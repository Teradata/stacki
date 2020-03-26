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
from stack.exception import ArgRequired, CommandError
from stack.commands import BoxArgProcessor

class Command(BoxArgProcessor, stack.commands.remove.command):
	"""
	Remove a box specification from the database.

	<arg type='string' name='box'>
	A list of boxes to remove.  Boxes must not have any hosts assigned.
	</arg>

	<example cmd='remove box test'>
	Removes the box named "test" from the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'box')

		boxes = self.get_box_names(args)

		# Prevent user from removing the default box.
		if 'default' in boxes:
			raise CommandError(self, 'cannot remove default box')

		# Check if the box is associated with any hosts
		for box in boxes:
			for row in self.call('list.host'):
				if row['box'] == box:
					raise CommandError(
						self,
						f'cannot remove box "{box}" because '
						f'host "{row["host"]}" is assigned to it'
					)

		# Safe to delete the boxes
		for box in boxes:
			self.db.execute('delete from boxes where name=%s', (box,))
