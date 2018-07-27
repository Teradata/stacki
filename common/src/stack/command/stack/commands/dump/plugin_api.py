# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'api'

	def run(self, args):

		if args and 'api' not in args:
			return

		# if there is no data, use an empty list as a placeholder.

		document_prep = {'api':[]}

		# grab all of the api groups
		api_group_data = self.owner.call('list.api.group')
		api_group_prep = []
		if api_group_data:
			# group['USERS'] is a ' ' delimeted string we need to turn into a list
			api_group_prep = {group['GROUP']: {'users': [user for user in group['USERS'].split()]} for group in api_group_data}
			# now that we have all of the groups, get each groups permission data
			for group, data in api_group_prep.items():
				api_group_perm_data = self.owner.call('list.api.group.perms', [ group ])
				if api_group_perm_data:
					data['permissions'] = [item['Command'] for item in api_group_perm_data]
				else:
					data['permissions'] = []

		# grab all of the api users
		api_user_data = self.owner.call('list.api.user')
		api_user_prep = []
		if api_user_data:
			api_user_prep = api_user_data
			# now that we have all of the users, get each user's permission and group data
			for user in api_user_prep:
				# reset the ' ' delimeted string of groups to a list
				user['groups'] = user['groups'].split()
				api_user_perm_data = self.owner.call('list.api.user.perms', [ user['username'] ])
				if api_user_perm_data:
					# we don't want to include group inherited permissions in this section, we already have them above
					# the only other permission scope is user, so we don't need to bother listing each source either
					user['permissions'] = [item['Command'] for item in api_user_perm_data if item['Source'] != 'G']
				else:
					user['permissions'] = []

		# grab all of the blacklisted api commands
		blacklist_command_data = self.owner.call('list.api.blacklist.command')
		blacklist_command_prep = []
		if blacklist_command_data:
			blacklist_command_prep = [command['Command'] for command in blacklist_command_data]


		document_prep['api'] = {
					'group':api_group_prep,
					'user':api_user_prep,
					'blacklist commands':blacklist_command_prep
					}

		return(document_prep)


