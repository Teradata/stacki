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
from stack.exception import ArgUnique


class Command(stack.commands.list.host.command):
	"""
	Lists the monolithic XML configuration file for a host.
	Tis is the same XML configuration file that is sent back to a 
	host when a host begins its installation procedure.

	<arg optional='1' type='string' name='host'>
	Hostname for requested XML document.
	</arg>

	<example cmd='list host xml backend-0-0'>
	List the XML configuration file for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		(pallet, debug ) = self.fillParams([
			('pallet', ),
			('debug', 'false')
		])

		debug = self.str2bool(debug)

		hosts = self.getHostnames(args)
		if len(hosts) != 1:
			raise ArgUnique(self, 'host')
		host = hosts[0]
		
		self.beginOutput()

		# Call "stack list node xml" with attrs{} dictionary
		# set from the database.


		attrs = {}
		for row in self.call('list.host.attr', [ host ]):
			attrs[row['attr']] = row['value']

		args = [ attrs['node'] ]
		args.append('attrs=%s' % attrs)
		if pallet:
			args.append('pallet=%s' % pallet)
		xml = self.command('list.node.xml', args)
		if not debug:
			for line in xml.split('\n'):
				self.addOutput(host, line)

		self.endOutput(padChar='', trimOwner=True)
