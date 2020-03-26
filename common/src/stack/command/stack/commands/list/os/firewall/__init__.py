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

class Command(NetworkArgProcessor, stack.commands.list.os.command):
	"""
	List the firewall rules for an OS.

	<arg optional='1' type='string' name='os' repeat='1'>
	Zero, one or more OS names. If no OS names are supplied, the firewall
	rules for all OSes are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.firewall', self._argv + ['scope=os'], verbose_errors = False))
		return self.rc
