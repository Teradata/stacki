# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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


class Command(stack.commands.set.host.command):
	"""
	Set the rank number for a list of hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='rank' optional='0'>
	The rank number to assign to each host.
	</param>

	<example cmd='set host rank backend-0-2 rank=2'>
	Set the rank number to 2 for backend-0-2.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(rank, ) = self.fillParams([
			('rank', None, True)
		])

		for host in hosts:
			self.db.execute(
				'update nodes set rank=%s where name=%s',
				(rank, host)
			)
