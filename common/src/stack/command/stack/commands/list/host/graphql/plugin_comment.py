# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin, stack.commands.list.command):

	def provides(self):
		return 'comment'

	def requires(self):
		return ['basic', 'redis_status', 'hash_status']

	def run(self, args):
		(hosts, expanded, hashit) = args

		host_info = dict.fromkeys(hosts)

		results = self.graphql(query_string = """
		{
			nodes {
				name: Name
				comment: Comment
			}
		}
		""")

		for host in results['nodes']:
			host_name = host.get('name')
			if host_name in host_info:
				host_info[host_name] = (host.get('comment'),)

		return {'keys'  : ['comment',],
			'values': host_info }
