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
import subprocess


class Command(stack.commands.sync.command):
	"""
	Rebuild the DNS configuration files, then restart named.

	<example cmd='sync dns'>
	Rebuild the DNS configuration files, then restart named.
	</example>
	"""

	def run(self, params, args):

		self.notify('Sync DNS\n')
		self.runPlugins()
		subprocess.call(['systemctl','restart','named'])
