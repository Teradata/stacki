# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.add.host.command):
	"""
	Adds an attribute to a host and sets the associated values

	<arg type='string' name='host' optional='0' repeat='1'>
	Host name of machine
	</arg>

	<param type='string' name='attr' optional='0'>
	Name of the attribute
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>

	<param type='boolean' name='shadow'>
	If set to true, then set the 'shadow' value (only readable by root
	and apache).
	</param>

	<example cmd='set host attr backend-0-0 attr=cpus value=2'>
	Sets the number of cpus of backend-0-0 to 2
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		self.command('set.host.attr', self._argv + ['force=no'], verbose_errors = False)
		return self.rc
