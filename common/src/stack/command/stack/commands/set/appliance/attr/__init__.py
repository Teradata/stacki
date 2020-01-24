# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.set.appliance.command):
	"""
	Sets an attribute to an appliance and sets the associated values

	<arg type='string' name='appliance' optional='0' repeat='1'>
	Name of appliance
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

	<example cmd='set appliance attr backend attr=sge value=False'>
	Sets the sge attribution to False for backend appliances
	</example>
	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'appliance')

		self.command('set.attr', self._argv + ['scope=appliance'], verbose_errors = False)
		return self.rc
