# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.topo import Redis
import stack.commands
import redis
import json

class Plugin(stack.commands.Plugin):

	def requires(self):
		return ['basic', 'redis_status']
	
	def provides(self):
		return 'hash_status'

	def run(self, args):
		(hosts, expanded, hashit) = args

		ret_val = {'keys': [], 'values': {}}

		if not hashit:
			return ret_val

		hash_status = dict.fromkeys(hosts)

		ids = {}
		for name, id in self.db.select('name, id from nodes'):
			ids[name] = id

		for host in hosts:
			try:
				r = redis.StrictRedis(host=Redis.server)
				status = r.get('host:%d:installhash' % ids[host])
			except:
				status = None

			if status:
				hashinfo = status.decode()
				onhost = json.loads(hashinfo.replace("'", '"'))

				computed = []

				output = self.owner.command('list.host.hash', [ host, 'profile=y' ])
				for o in output.split('\n'):
					line = o.split()
					if len(line) == 2:
						hashline = {}
						hashline['name'] = line[1]
						hashline['hash'] = line[0]
						computed.append(hashline)

				if computed == onhost:
					status = 'synced'
				else:
					status = 'notsynced'

			hash_status[host] = ( status, )

		r = { 'keys' : [ 'hash' ], 'values': hash_status }
		return r

