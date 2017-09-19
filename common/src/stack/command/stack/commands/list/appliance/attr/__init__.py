# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.list.appliance.command):
	"""
	Lists the set of attributes for appliances.

	<arg optional='1' type='string' name='appliance'>
	Name of appliance
	</arg>
	
	<example cmd='list appliance attr compute'>
	List the attributes for compute appliances
	</example>
	"""

	def run(self, params, args):
		self.addText(self.command('list.attr', self._argv + [ 'scope=appliance' ]))
		return self.rc

