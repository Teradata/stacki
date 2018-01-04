# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.attr
import stack.commands


class Command(stack.commands.dump.appliance.command):
	"""
	Dump the set of attributes for appliances.

	<arg optional='1' type='string' name='appliance'>
	Name of appliance
	</arg>
	
	<example cmd='dump appliance attr backend'>
	List the attributes for backend appliances
	</example>
	"""

	def run(self, params, args):

		for row in self.call('list.appliance.attr', args):
			app = row['appliance']
			t   = row['type']
			a   = row['attr']
			v   = self.quote(row['value'])
			
			if t == 'const':
				continue

			s = ''
			if t == 'shadow':
				s = 'shadow=true'

			self.dump('"set attr" scope=appliance object=%s force=false attr=%s value=%s %s' % (app, a, v, s))


