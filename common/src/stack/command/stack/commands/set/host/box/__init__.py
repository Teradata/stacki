# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import BoxArgProcessor

class Command(BoxArgProcessor, stack.commands.set.host.command):
	"""
	Sets the box for a list of hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='box' optional='0'>
	The name of the box (e.g. default)
	</param>

	<example cmd='set host box backend box=default'>
	Set the box for all backend nodes to default.
	</example>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		box, = self.fillParams([
			('box', None, True)
		])

		# Check to make sure this is a valid box name
		self.get_box_names([ box ])

		for host in hosts:
			self.db.execute("""
				update nodes set box=(
					select id from boxes where name=%s
				) where name=%s
			""", (box, host))
