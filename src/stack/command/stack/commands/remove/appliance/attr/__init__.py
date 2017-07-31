# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.attr
import stack.commands
from stack.exception import *

class Command(stack.commands.remove.appliance.command):
	"""
	Remove an attribute for an appliance.

	<arg type='string' name='appliance' optional='1' repeat='1'>
	One or more appliances
	</arg>
	
	<param type='string' name='attr' optional='0'>
	The attribute name that should be removed.
	</param>
	
	<example cmd='remove appliance attr backend attr=sge'>
	Removes the attribute sge for backend appliances
	</example>
	"""

	def run(self, params, args):
		self.command('set.attr', self._argv + [ 'scope=appliance', 'value=' ])
		return self.rc
