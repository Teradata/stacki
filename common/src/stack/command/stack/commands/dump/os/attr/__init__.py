# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.attr
import stack.commands


class Command(stack.commands.dump.os.command):
	"""
	Dump the set of attributes for the OS

	<arg optional='1' type='string' name='os' repeat='1'>
	Zero, one or more os names
	</arg>

	<example cmd='dump os attr redhat'>
	Dump attribute information for redhat os.
	</example>
	"""

	def run(self, params, args):
		
		for row in self.call('list.os.attr', args):
			o = row['os']
			t = row['type']
			a = row['attr']
			v = self.quote(row['value'])
			
			if t == 'const':
				continue

			s = ''
			if t == 'shadow':
				s = 'shadow=true'

			self.dump('"set attr" scope=environment object=%s force=false attr=%s value=%s %s' % (o, a, v, s))

