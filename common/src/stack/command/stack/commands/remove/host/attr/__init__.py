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


class Command(stack.commands.remove.host.command):
	"""
	Remove an attribute for a host.

	<arg type='string' name='host' optional='1' repeat='1'>
	One or more hosts
	</arg>

	<param type='string' name='attr' optional='0'>
	The attribute name that should be removed.
	</param>

	<example cmd='remove host attr backend-0-0 attr=cpus'>
	Removes the attribute cpus for host backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.command('remove.attr', self._argv + ['scope=host'])
		return self.rc
