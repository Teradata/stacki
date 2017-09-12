# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.BoxArgumentProcessor,
	stack.commands.remove.command):
	"""
	Remove a box specification from the database.

	<arg type='string' name='box'>
	Box name.
	</arg>
	
	<example cmd='remove box test'>
	Removes the box named "test" from the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, 'box')

		boxes = self.getBoxNames(args)

		# Prevent user from removing the default box.
		
		if 'default' in boxes:
			raise CommandError(self, 'cannot remove default box')

		# first check if the box is associated with any hosts

		for box in boxes:
			for row in self.call('list.host'):
				if row['box'] == box:
					raise CommandError(self, 'cannot remove box "%s"\nbecause host "%s" is assigned to this box' % (box, row['host']))

		for box in boxes:
			self.db.execute("""delete from boxes
				where name = '%s' """ % box)

