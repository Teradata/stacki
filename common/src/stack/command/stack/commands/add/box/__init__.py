# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack
import stack.commands
from stack.exception import ArgUnique, CommandError


class Command(stack.commands.BoxArgumentProcessor,
	stack.commands.add.command):
	"""
	Add a box specification to the database.

	<arg type='string' name='box'>
	Name of the new box.
	</arg>
	
	<param type='string' name='os'>
	OS associated with the box. Default is 'redhat'
	</param>

	<example cmd='add box develop'>
	Adds the box named "develop" into the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'box')

		box = args[0]
		
		if box in self.getBoxNames():
			raise CommandError(self, 'box "%s" exists' % box)

		OS, = self.fillParams([ ('os', 'redhat') ])

		self.db.execute("""insert into boxes (name, os) values
			('%s', (select id from oses where name='%s'))""" % (box, OS))

