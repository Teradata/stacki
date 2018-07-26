# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError

class Plugin(stack.commands.Plugin, stack.commands.Command):
	notifications = True

	def provides(self):
		return 'api'
	def requires(self):
		return [ 'software', 'environment', 'group', 'network', 'appliance', 'os', 'global', 'host', 'bootaction' ]
	def run(self, args):

		# check if the user would like to import api data
		if args and 'api' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		if 'api' in self.owner.data:
			import_data = self.owner.data['api']
		else:
			self.owner.log.info.info('no api data in json file')
			return

		self.notify('\n\tLoading api\n')

		# load the api group information
		for group, data in import_data['group'].items():
			try:
				self.owner.command('add.api.group', [ group ])
				self.owner.successes += 1
				self.owner.log.info(f'success adding api group {group}')
			except CommandError as e:
				if 'already' in str(e):
					self.owner.log.info(f'warning adding api group {group}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error affing api group {group}: {e}')
					self.owner.errors += 1
			# add the permissions for the group
			for permission in data['permissions']:
				try:
					self.owner.command('add.api.group.perms', [ group, f'perm={permission}' ])
					self.owner.successes += 1
					self.owner.log.info(f'success adding {permission} perm to {group}')
				except CommandError as e:
					if 'already' in str(e):
						self.owner.log.info(f'warning adding {permission} perm to {group}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding {permission} perm to {group}')
						self.owner.warnings += 1

		# load the api user information
		for user in import_data['user']:
			try:
				self.owner.command('add.api.user', [
								user['username'],
								f'admin={user["admin"]}',
								# just add the first group for now, we will add the others later
								f'group={user["groups"][0]}'
								])
				self.owner.successes += 1
				self.owner.log.info(f'success adding user {user["username"]}')
			except CommandError as e:
				if 'already' in str(e):
					self.owner.log.info(f'warning adding user {user["username"]}')
					self.owner.warnings += 1
				else:
					self.owner.log.info(f'error adding user {user["username"]}: {e}')
					self.owner.errors += 1
			# now we iterate through each users groups
			for group in user['groups']:
				try:
					self.owner.command('add.api.user.group', [
									user['username'],
									f'group={group}'
									])
					self.owner.successes += 1
					self.owner.log.info(f'success adding user {user["username"]} to group {group}')
				except CommandError as e:
					if 'already' in str(e):
						self.owner.log.info(f'warning adding user {user["username"]} to group {group}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding user {user["username"]} to group {group}: {e}')
						self.owner.errors += 1
			# now we add user level permissions
			for permission in user['permissions']:
				try:
					self.owner.command('add.api.user.perms', [
										user['username'],
										f'perm={permission}'
										])
					self.owner.successes += 1
					self.owner.log.info(f'success adding permission {permission} to user {user["username"]}')
				except CommandError as e:
					if 'already' in str(e):
						self.owner.log.info(f'warning adding permission {permission} to user {user["username"]}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding permission {permission} to user {user["username"]}')
						self.owner.errors += 1

		# load the blacklisted commands
		for blacklist_command in import_data['blacklist commands']:
			try:
				self.owner.command('add.api.blacklist.command', [ f'command={blacklist_command}' ])
				self.owner.successes += 1
				self.owner.log.info(f'success adding blacklist command {blacklist_command}')
			except CommandError as e:
					if 'already' in str(e):
						self.owner.log.info(f'warning adding blacklist command {blacklist_command}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding blacklist command {blacklist_command}: {e}')
						self.owner.errors += 1
