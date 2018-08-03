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
		if (not args or 'host' in args) and 'host' in self.data:
			current_frontend = json.loads(self.command('list.host', [ 'a:frontend', 'output-format=json' ]))[0]['host']
			for host in self.data['host']:
				if host['appliance'] == 'frontend' and host['name'] != current_frontend:
					raise CommandError(self, 'frontend name in the json document does not match the current frontend name')

		# Make sure that all of the pallets at least have URLs
		if (not args or 'software' in args) and 'software' in self.data and 'pallet' in self.data['software']:
			for pallet in self.data['software']['pallet']:
				if pallet['url'] == None:
					raise CommandError(self, f'pallet {pallet["name"]} {pallet["version"]} has no url')


	# 'command' and 'parameters' are the same as a usual self.command call
	# command_description is the string that will be printed in the logs, for example: f'adding host {hostname}'
	# warning_string is used to filter CommandErrors, checking to see if the error is simply that the item already exists in the database
	# the two warning_strings that are being used curently are 'already' and 'exists'
	# try_command returns a return code to indicate if the command was successful
	def try_command(self, command, parameters, action_description, warning_string):
		try:
			self.command(command, parameters)
			self.log.info(f'success {action_description}')
			self.successes += 1
			return 0

		except CommandError as e:
			if warning_string in str(e):
				self.log.info(f'warning {action_description}: {e}')
				self.warnings += 1
				return 1
			else:
				self.log.info(f'error {action_description}: {e}')
				raise CommandError(self, f'error {action_description}: {e}')


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
		s = subprocess.run(['/etc/cron.daily/backup-cluster-db'])
		if s.returncode != 0:
			raise CommandError(self, 'unable to backup the cluster database, aborting')

		# so that we are able to report how successful the load was
		self.successes = 0
		self.warnings = 0
		self.errors = 0

		# start a logger
		self.log = logging.getLogger("load-json")
		logging.basicConfig(filename='/var/log/load-json.log', filemode='w+', level=logging.INFO)

		try:
			self.runPlugins(args)
		except CommandError as e:
			self.log.info(f'Load terminated early: {e}')
			self.errors += 1

		# report how well the load went
		self.notify(f'\nload finished with:\n{self.successes} successes\n{self.warnings} warnings\n{self.errors} errors\nCheck /var/log/load-json.log for details.\n')

		# if there are errors, revert db changes and raise a CommandError
		if self.errors != 0:
			self.notify('\nThere were errors during the load, restoring the database. Check /var/log/load-json.log for details.\n')
			s = subprocess.run(['bash', '/var/db/restore-stacki-database.sh'])
			if s.returncode != 0:
				raise CommandError(self, 'There were errors and the database could not be restored. Check /var/log/load-json.log for details')

			raise CommandError(self, 'The database has been restored. No changes have been made.')
