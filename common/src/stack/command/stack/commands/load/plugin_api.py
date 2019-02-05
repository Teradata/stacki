# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError

class __Plugin(stack.commands.Plugin, stack.commands.Command):
	def provides(self):
		return 'api'
	def requires(self):
		return [ 'software', 'environment', 'group', 'network', 'appliance', 'os', 'global', 'bootaction', 'host' ]
	def run(self, args):

		# check if the user would like to import api data
		if args and 'api' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'api' in self.owner.data:
			import_data = self.owner.data['api']
		else:
			self.owner.log.info('no api data in json file')
			return

		self.notify('\n\tLoading api')

		# load the api group information
		for group, data in import_data['group'].items():
			self.owner.try_command('add.api.group', [ group ], f'adding api group {group}', 'already')

			for permission in data['permissions']:
				self.owner.try_command('add.api.group.perms', [ group, f'perm={permission}' ], f'adding api group permission {permission}', 'already')

		# load the api user information
		for user in import_data['user']:
			parameters = [
				user['username'],
				f'admin={user["admin"]}',
				# just add the first group for now, we will add the others later
				f'group={user["groups"][0]}'
				]
			self.owner.try_command('add.api.user', parameters, f'adding api user {user["username"]}', 'already')

		# now we iterate through each users groups
			for group in user['groups']:
				parameters = [
					user['username'],
					f'group={group}',
					]
				self.owner.try_command('add.api.user.group', parameters, f'adding api user group {group}', 'already')

			# now we add user level permissions
			for permission in user['permissions']:
				parameters = [
					user['username'],
					f'perm={permission}',
					]
				self.owner.try_command('add.api.user.perms', parameters, f'adding permission {permission} to user {user["username"]}', 'already')

		# load the blacklisted commands
		for blacklist_command in import_data['blacklist commands']:
			self.owner.try_command('add.api.blacklist.command', [ f'command={blacklist_command}' ], f'adding blacklist command {blacklist_command}', 'already')
