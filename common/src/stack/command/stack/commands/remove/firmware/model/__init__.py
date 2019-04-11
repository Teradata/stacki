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
	Removes a firmware model from the stacki database.

	<arg type='string' name='model' repeat='1'>
	One or more model names to remove. Any firmware associated with the models will also be removed.
	</arg>

	<param type='string' name='make'>
	The maker of the models being removed. This must correspond to an already existing make.
	</param>

	<example cmd="remove firmware model awesome_9001 mediocre_5200 make='boss hardware corp'">
	Removes two models with the names 'awesome_9001' and 'mediocre_5200' from the set of available firmware models under the 'boss hardware corp' make.
	This also removes any firmware associated with those models.
	</example>
	"""

	def run(self, params, args):
		self.runPlugins(args = (params, args))
