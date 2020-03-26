# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import NetworkArgProcessor

class Command(NetworkArgProcessor, stack.commands.list.environment.command):
	"""
	List the firewall rules for a given environment.

	<arg optional='1' type='string' name='environment' repeat='1'>
	Zero or more environments. If no environments are supplied,
	the firewall rules for all environments are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.firewall', self._argv + ['scope=environment'], verbose_errors = False))
		return self.rc
