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

import stack.file
import stack.commands


class Command(stack.commands.sync.command):
	"""
	For each system configuration file controlled by Stack, first
	rebuild the configuration file by extracting data from the
	database, then restart the relevant services.

	<example cmd='sync config'>
	Rebuild all configuration files and restart relevant services.
	</example>
	"""

	def run(self, params, args):

		self.notify('Sync Config')

		self.runPlugins()
