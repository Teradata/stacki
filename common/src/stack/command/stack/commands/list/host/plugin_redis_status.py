# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def requires(self):
		return ['basic']
	
	def provides(self):
		return 'redis_status'

	def run(self, args):
		(hosts, expanded, hashit) = args

		# stack list host status replaces this

		host_status = dict.fromkeys(hosts)
		for host in hosts:
			host_status[host] = ( 'deprecated', )

		return { 'keys' : [ 'status' ], 'values': host_status }
