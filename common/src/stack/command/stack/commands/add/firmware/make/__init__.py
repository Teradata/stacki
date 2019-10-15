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

class Command(stack.commands.add.firmware.command):
	"""
	Adds firmware makes to the stacki database.

	<arg type='string' name='make' repeat='1'>
	One or more make names to add. Make names are required to be unique, and any duplicates will be ignored.
	</arg>

	<example cmd="add firmware make mellanox dell">
	Adds two makes with the names 'mellanox' and 'dell' to the set of available firmware makes.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
