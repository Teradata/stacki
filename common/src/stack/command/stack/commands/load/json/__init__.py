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
import json
import sys
import os
from stack.exception import CommandError

class command(stack.commands.load.command, stack.commands.Command):
	MustBeRoot = 0


class Command(command):
	"""
	Load configuration data from the provided json document. If no arguments
	are provided then all plugins will be run.

	<param optional='1' type='string' name='file'>
	The json document containing the configuration information.
	</param>

	<arg optional='0' type='string' name='software'>
	Load pallet, cart, and box data. If the pallet exists on a remote
	server that requires authentication, be sure to provide the username
	and password in the corresponding json fields.
	</arg>

	<arg optional='0' type='string' name='host'>
	Load name, rack, rank, interface, attr, firewall, box, appliance,
	comment, metadata, environment, osaction, route, group, partition,
	and controller data for each host.
	</arg>

	<arg optional='0' type='string' name='network'>
	Load name, address, gateway, netmask, dsn, pxe, mtu, and zone
	data for each network.
	</arg>

	<arg optional='0' type='string' name='global'>
	Load attr, route, firewall, partition, and controller data for
	the global scope.
	</arg>

	<arg optional='0' type='string' name='os'>
	Load name, attr, route, firewall, partition, and controller
	data for each os.
	</arg>

	<arg optional='0' type='string' name='appliance'>
	Load name, attr, route, firewall, partition, and controller
	data for each appliance.
	</arg>

	<arg optional='0' type='string' name='group'>
	Load name data for each group.
	</arg>

	<arg optional='0' type='string' name='bootaction'>
	Load name, kernel, ramdisk, type, arg, and os data for each
	bootaction.
	</arg>
	"""
	def checks(self, args):

		# check to make sure that the user is not attepting to add more than one frontend
		if ('host' in args or not args) and 'host' in self.data:
			current_frontend = json.loads(self.command('list.host', [ 'a:frontend', 'output-format=json' ]))[0]['host']
			for host in self.data['host']:
				if host['appliancelongname'] == 'Frontend' and host['name'] != current_frontend:
					raise CommandError(self, 'frontend name in the json document does not match the current frontend name')


	def run(self, params, args):

		filename, = self.fillParams([
		('file', None, True),
		])

		if not os.path.exists(filename):
			raise CommandError(self, f'file {filename} does not exist')

		with open (os.path.abspath(filename), 'r') as file:
			try:
				self.data = json.load(file)
			except ValueError:
				raise CommandError(self, 'Invalid json document')

		self.checks(args)

		self.successes = 0
		self.warnings = 0
		self.errors = 0

		self.runPlugins(args)

		print(f'\nload finished with:\n{self.successes} successes\n{self.warnings} warnings\n{self.errors} errors')
		if self.errors != 0:
			raise CommandError(self, 'There was at least one error')

