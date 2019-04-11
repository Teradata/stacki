# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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

class Command(stack.commands.remove.firmware.command):
	"""
	Removes firmware makes from the stacki database.

	<arg type='string' name='make' repeat='1'>
	One or more make names to remove. This will also remove any associated models and firmware associated with those models.
	</arg>

	<example cmd="remove firmware make mellanox dell">
	Removes two makes with the names 'mellanox' and 'dell'. This also removes any associated models and firmware associated with the models removed.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
