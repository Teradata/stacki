# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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


class Command(stack.commands.dump.host.command):
	"""
	Dump the set of attributes for hosts.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='dump host attr backend-0-0'>
	Dump the attributes for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		for row in self.call('list.host.attr', args):
			host	= row['host']
			s	= row['scope']
			t	= row['type']
			a	= row['attr']
			v	= self.quote(row['value'])
			
			if t == 'const' or s != 'host':
				continue

			flag = ''
			if t == 'shadow':
				flag = 'shadow=true'

			self.dump('"set attr" scope=host %s force=false attr=%s value=%s %s' % (host, a, v, flag))


