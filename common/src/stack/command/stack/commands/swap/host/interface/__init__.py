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
from stack.exception import CommandError


class Command(stack.commands.swap.host.command):
	"""
	Swaps two host interfaces in the database.

	<arg type='string' name='host' optional='0' repeat='1'>
	Host name of machine
	</arg>

	<param type='string' name='interfaces' optional='0'>
	Two comma-separated interface names (e.g., interfaces="eth0,eth1").
	</param>

	<param type='boolean' name='sync-config'>
	If "yes", then run 'stack sync host config' and 'stack sync host network'
	at the end of the command. The default is: yes.
	</param>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		interfaces, sync_config = self.fillParams([
			('interfaces', None, True),
			('sync-config', 'yes')
		])

		sync_config = self.str2bool(sync_config)

		interface = interfaces.split(',')
		if len(interface) != 2:
			raise CommandError(self, 'must supply exactly two interfaces')

		for host in hosts:
			# Get the data for our two interfaces to swap
			rows = self.db.select("""
				id, device, mac, module, options FROM networks
				WHERE node=(select id from nodes where name=%s)
				AND device in (%s, %s)
			""", (host, *interface))

			# We gotta have two interfaces to swap
			if len(rows) != 2:
				raise CommandError(
					self, 'one or more of the interfaces are missing'
				)

			# Swap the first interface
			self.db.execute("""
				UPDATE networks
				SET device=%s, mac=%s, module=%s, options=%s
				WHERE id=%s
			""", (*rows[1][1:], rows[0][0]))

			# And now the second
			self.db.execute("""
				UPDATE networks
				SET device=%s, mac=%s, module=%s, options=%s
				WHERE id=%s
			""", (*rows[0][1:], rows[1][0]))

		if sync_config:
			self.command('sync.host.config', hosts)
			self.command('sync.host.network', hosts)
