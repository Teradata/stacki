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

	def run(self, hosts):
		host_status = dict.fromkeys(hosts)
		
		frontend_list = []
		frontend_list.append('localhost')

		# If we have the redis module try to find the frontend
		# on which the Redis server is running.

		validRedisConnection = False
		ret_val = {'keys': [], 'values': {}}
		try:
			import redis
		except:
			return ret_val
		
		for frontend in frontend_list:
			try:
				r = redis.StrictRedis(host=frontend)
				validRedisConnection = True
				break
			except:
				pass

		if not validRedisConnection:
			return ret_val

		for host in hosts:
			try:
				status = r.get('host:%s:status' % host) 
			except:
				status = None
			if status:
				status = status.decode()
			host_status[host] = ( status, )

		r = { 'keys' : [ 'status' ], 'values': host_status }
		return r
