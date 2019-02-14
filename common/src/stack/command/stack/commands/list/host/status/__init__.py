# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.topo import Redis
from stack.exception import CommandError
import stack.commands


class command(stack.commands.list.host.command):
	pass
	

class Command(command):
	"""
	List the Status information for one or more hosts.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>
	"""
	def run(self, params, args):

		import redis # not part of the installer but command line is
		try:
			r = redis.StrictRedis(host=Redis.server)
		except:
			raise CommandError(self, 'cannot connect to redis')

		ids = {}
		for name, id in self.db.select('name, id from nodes'):
			ids[name] = id

		components = []
		for (_, names) in self.runPlugins():
			components.extend(names)

		self.beginOutput()

		for host in self.getHostnames(args):
			status = []
			for component in components:
				try:
					v = r.get('host:%d:status:%s' % (ids[host], component))
				except redis.exceptions.ConnectionError:
					v = None
				if v is not None:
					v = v.decode()
				status.append(v)
			self.addOutput(host, status)

		header = [ 'host' ]
		header.extend(components)
		self.endOutput(header=header, trimOwner=False)

