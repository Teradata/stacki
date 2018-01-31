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

import stack.commands


class Command(stack.commands.dump.host.command):
	"""
	Dump the host interface information as stack commands.
		
	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, 
	information for all hosts will be listed.
	</arg>

	<example cmd='dump host interface backend-0-0'>
	Dump the interfaces for backend-0-0.
	</example>

	<example cmd='dump host interface backend-0-0 backend-0-1'>
	Dump the interfaces for backend-0-0 and backend-0-1.
	</example>

	<example cmd='dump host interface'>
	Dump all interfaces.
	</example>
		
	"""

	def run(self, params, args):

		for dict in self.call('list.host.interface'):

			if not dict['interface']:
				continue # skip unconfigured dicts
				 
			if dict['host'] == self.db.getHostname():
				continue # skip frontend

			self.dump('"add host interface" %s interface=%s' %
				(dict['host'], dict['interface']))

			for option in dict.keys():
				if option == 'host':
					continue
				if dict[option]:
					self.dump('"set host interface %s" %s %s=%s' %
						(option, dict['host'], option, dict[option]))

