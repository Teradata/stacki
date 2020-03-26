# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import ApplianceArgProcessor
from stack.exception import CommandError


class Command(ApplianceArgProcessor, stack.commands.set.host.command):
	"""
	Set the Appliance for a list of hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='appliance' optional='0'>
	Appliance name (e.g. "backend").
	</param>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(appliance, ) = self.fillParams([
			('appliance', None, True)
		])

		if appliance not in self.getApplianceNames():
			raise CommandError(self, 'appliance parameter not valid')

		for host in hosts:
			self.db.execute("""
				update nodes set appliance=(
					select id from appliances where name=%s
				)
				where name=%s
			""", (appliance, host))
