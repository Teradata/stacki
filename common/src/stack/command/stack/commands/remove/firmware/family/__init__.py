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
	Removes a firmware family to the stacki database.

	<arg type='string' name='family' repeat='1'>
	One or more family names to remove. This will also remove any firmware associated with this family.
	</arg>

	<example cmd="remove firmware family my_awesome_family my_less_awesome_inlaws">
	Removes two families with the names 'my_awesome_family' and 'my_less_awesome_inlaws' and all firmware files associated with them.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = args)
