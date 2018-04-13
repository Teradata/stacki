# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import stack.attr
import stack.commands


class Command(stack.commands.dump.command):
	"""
	Dump the set of attributes

	<example cmd='dump attr'>
	Dump the set of all global attributes
	</example>	
	"""

	def run(self, params, args):

		for row in self.call('list.attr'):
			t = row['type']
			a = row['attr']
			v = self.quote(row['value'])
			
			if t == 'const':
				continue

			s = ''
			if t == 'shadow':
				s = 'shadow=true'

			self.dump('"set attr" scope=global force=false attr=%s value=%s %s' % (a, v, s))

