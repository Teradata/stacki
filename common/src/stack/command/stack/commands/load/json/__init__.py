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
import subprocess
import logging
import stack.commands

class command(stack.commands.load.command, stack.commands.Command):
	MustBeRoot = 0
	notifications = True


class Command(command):
	"""
	Load configuration data from the provided json document. If no arguments
	are provided then all plugins will be run.

	<param optional='0' type='string' name='file'>
	The json document containing the configuration information.
	</param>

	<arg optional='1' type='string' name='software'>
	Load pallet, cart, and box data. If the pallet exists on a remote
	server that requires authentication, be sure to provide the username
	and password in the corresponding json fields.
	</arg>

	<arg optional='1' type='string' name='host'>
	Load name, rack, rank, interface, attr, firewall, box, appliance,
	comment, metadata, environment, osaction, route, group, partition,
	and controller data for each host.
	</arg>

	<arg optional='1' type='string' name='network'>
	Load name, address, gateway, netmask, dsn, pxe, mtu, and zone
	data for each network.
	</arg>

	<arg optional='1' type='string' name='global'>
	Load attr, route, firewall, partition, and controller data for
	the global scope.
	</arg>

	<arg optional='1' type='string' name='os'>
	Load name, attr, route, firewall, partition, and controller
	data for each os.
	</arg>

	<arg optional='1' type='string' name='appliance'>
	Load name, attr, route, firewall, partition, and controller
	data for each appliance.
	</arg>

	<arg optional='1' type='string' name='group'>
	Load name data for each group.
	</arg>

	<arg optional='1' type='string' name='bootaction'>
	Load name, kernel, ramdisk, type, arg, and os data for each
	bootaction.
	</arg>
	"""

	def checks(self, args):

		# Make sure that the user is not attepting to add more than one frontend
		if ('host' in args or not args) and 'host' in self.data:
			current_frontend = json.loads(self.command('list.host', [ 'a:frontend', 'output-format=json' ]))[0]['host']
			for host in self.data['host']:
				if host['appliance'] == 'frontend' and host['name'] != current_frontend:
					raise CommandError(self, 'frontend name in the json document does not match the current frontend name')

		# Make sure that all of the pallets at least have URLs
		if ('software' in args or not args) and 'software' in self.data and 'pallet' in self.data['software']:
			for pallet in self.data['software']['pallet']:
				if pallet['url'] == None:
					raise CommandError(self, f'pallet {pallet["name"]} {pallet["version"]} has no url')


	def run(self, params, args):

		filename, = self.fillParams([
			('file', None, True),
		])

		if not os.path.exists(filename):
			raise CommandError(self, f'file {filename} does not exist')

		with open (os.path.abspath(filename), 'r') as f:
			try:
				self.data = json.load(f)
			except ValueError:
				raise CommandError(self, 'Invalid json document')

		# run a few pre checks
		self.checks(args)

		# make a backup of the database in its current state in the event of any errors
		s = subprocess.run(['mysqldump', 'cluster'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		with open ('cluster_backup.sql', 'wb+') as f:
			f.write(s.stdout)
		s = subprocess.run(['mysqldump', 'django'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		with open ('django_backup.sql', 'wb+') as f:
			f.write(s.stdout)

		# so that we are able to report how successful the load was
		self.successes = 0
		self.warnings = 0
		self.errors = 0

		# start a logger
		self.log = logging.getLogger("load-json")
		logging.basicConfig(filename='/var/log/load-json.log', filemode='w+', level=logging.INFO)

		self.runPlugins(args)

		# report how well the load went
		self.notify(f'\nload finished with:\n{self.successes} successes\n{self.warnings} warnings\n{self.errors} errors\n')

		# if there are errors, revert db changes and raise a CommandError
		if self.errors != 0:
			with open('cluster_backup.sql', 'rb') as f:
				cluster_backup = f.read()
			s = subprocess.Popen(['mysql', 'cluster'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			s.communicate(cluster_backup)
			with open('django_backup.sql', 'rb') as f:
				cluster_backup = f.read()
			s = subprocess.Popen(['mysql', 'django'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			s.communicate(cluster_backup)

			raise CommandError(self, 'There was at least one error, database has been reverted. No changes have been made.')
		else:
			# our load was successful so we can delete our temporary backup
			s = subprocess.call(['rm', '-f', 'cluster_backup.sql'], stdout=subprocess.PIPE)
