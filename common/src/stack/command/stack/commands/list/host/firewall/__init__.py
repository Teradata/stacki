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
from stack.commands import NetworkArgProcessor

class Command(NetworkArgProcessor, stack.commands.list.host.command):
	"""
	List the current firewall rules for the named hosts.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the
	firewall rules for all the known hosts are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.firewall', self._argv + ['scope=host'], verbose_errors = False))
		return self.rc
