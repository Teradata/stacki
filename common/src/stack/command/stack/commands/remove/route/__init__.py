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


class Command(stack.commands.remove.command):
	"""
	Remove a global static route.

	<param type='string' name='address' optional='0'>
	The address of the static route to remove.
	</param>

	<example cmd='remove route address=1.2.3.4'>
	Remove the global static route that has the network address '1.2.3.4'.
	</example>
	"""


	def run(self, params, args):

		(address, ) = self.fillParams([ ('address', None, True) ])

		self.db.execute("""delete from global_routes where 
			network = '%s'""" % address)

