# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import redis
import json

class Plugin(stack.commands.Plugin):

	def requires(self):
		return ['basic', 'redis_status']
	
	def provides(self):
		return 'hash_status'

	def run(self, hosts):
		ret_val = {'keys': [], 'values': {}}

		if not self.owner.hashit:
			return ret_val

		hash_status = dict.fromkeys(hosts)
		
		for host in hosts:
			try:
				r = redis.StrictRedis()
				status = r.get('host:%s:installhash' % host) 
			except:
				status = None

			if status:
				hashinfo = status.decode()
				onhost = json.loads(hashinfo.replace("'", '"'))

				computed = {}
				computed['hashes'] = []

				output = self.owner.command('list.host.hash', [ host, 'profile=y' ])
				for o in output.split('\n'):
					line = o.split()
					if len(line) == 2:
						hashline = {}
						hashline['name'] = line[1]
						hashline['hash'] = line[0]
						computed['hashes'].append(hashline)

				if computed == onhost:
					status = 'synced'
				else:
					status = 'notsynced'

			hash_status[host] = ( status, )

		r = { 'keys' : [ 'hash' ], 'values': hash_status }
		return r

