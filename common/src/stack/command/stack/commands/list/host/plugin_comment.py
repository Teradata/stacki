# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'comment'

	def requires(self):
		return ['basic', 'redis_status', 'hash_status']

	def run(self, args):
		(hosts, expanded, hashit) = args

		host_info = dict.fromkeys(hosts)

		for row in self.db.select(
			"""
			name, comment from nodes n
			"""):

			if row[0] in host_info:
				host_info[row[0]] = row[1:]

		return {'keys'  : ['comment',],
			'values': host_info }
