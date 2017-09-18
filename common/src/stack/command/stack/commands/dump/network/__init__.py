# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class command(stack.commands.NetworkArgumentProcessor,
	stack.commands.dump.command):
	pass
	

class Command(command):
	"""
	Dump the network information as rocks commands.

	<arg optional='1' type='string' name='network' repeat='1'>
	Zero, one or more network names. If no network names are supplied, 
	information for all networks will be listed.
	</arg>

	<example cmd='dump network'>
	Dump all network info.
	</example>
	
	<example cmd='dump network public'>
	Dump network info the 'public' network.
	</example>
	"""

	def run(self, params, args):

		for dict in self.call('list.network'):
			self.dump('"add network" %s' % dict['network'])
			 
			for option in dict.keys():
				if option == 'network':
					continue
				if dict[option]:
					self.dump('"set network %s" %s %s=%s' %
						(option, dict['network'], option, dict[option]))

