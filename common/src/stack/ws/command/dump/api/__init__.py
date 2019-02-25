# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict
import json


class Command(stack.commands.dump.command):

	def run(self, params, args):

		dump = OrderedDict(sudo      = [],
				   blacklist = [],
				   group     = [],
				   user      = [])

		group_info = {}
		for row in self.call('list.api.group'):
			group_info[row['group']] = []
					      
		for row in self.call('list.api.group.perms'):
			group_info[row['group']].append(row['command'])

		for group in group_info.keys():
			dump['group'].append(OrderedDict(
				name = group,
				perm = group_info[group]))


		user_info  = {}
		for row in self.call('list.api.user'):
			user_info[row['username']] = [self.str2bool(row['admin']),
						      row.get('groups', '').split(),
						      []]
					      
		for row in self.call('list.api.user.perms'):
			if row['source'] != 'G':
				user_info[row['user']][2].append(row['command'])

		for user in sorted(user_info.keys()):
			dump['user'].append(OrderedDict(
				name  = user,
				admin = user_info[user][0],
				group = user_info[user][1],
				perm  = user_info[user][2]))
		
		black_list = []
		for row in self.call('list.api.blacklist.command'):
			black_list.append(row['command'])
		dump['blacklist'] = sorted(black_list)

		sudo_list = []
		try:
			for row in self.call('list.api.sudo.command'):
				sudo_list.append(row['command'])
		except:
			pass # this fails on my host (probably just me)
		dump['sudo'] = sorted(sudo_list)



		self.addText(json.dumps(OrderedDict(version  = stack.version,
						    api      = dump), indent=8))

