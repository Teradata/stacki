# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import redis
import stack.api
import stack.mq.processors


class ProcessorBase(stack.mq.processors.ProcessorBase):
	"""
	Extends the stack.mq.processors.ProcessorBase to
	add support for creating Redis keys.  
	This is used to cache host information.
	"""

	def __init__(self, context, sock):
		self.redis = redis.StrictRedis()
		stack.mq.processors.ProcessorBase.__init__(self, context, sock)

	def isActive(self):
		return self.isMaster()

	def updateKey(self, key, value, timeout=None):
		"""
		Create an new *key* and *value* in the local Redis
		database with an optional *timeout*.  
		If the *key* already exist the value is blindly updated, and
		the *timeout* is reset if it is specified.

		:param key: redis key
		:type key: string
		:param value: key value
		:type value: string
		:param timeout: key timeout in seconds
		:type timeout: int
		"""
		self.redis.set(key, value)
		self.redis.expire(key, timeout)

	def updateHostKeys(self, client):
		"""
		Updates the Redis keys for a given host in the cluster.	 
		If Redis does not know about the host the cluster database is inspected and
		the keys are created with a one hour timeout.
		If Redis already contains the keys the timeout is reset.
		The following Redis keys are defined for the host::

			host:HOSTNAME:rack
			host:HOSTNAME:rank
			host:HOSTNAME:addr
			host:IPADDRESS:name

		:param addr: IP address
		:type addr: string
		:returns: dictionary with *name*, *addr*, *rack*, and *rank*
		"""
		if not client:
			client = '127.0.0.1'

		host = self.redis.get('host:%s:name' % client)
		if host:
			host = host.decode()
			rack = self.redis.get('host:%s:rack' % host).decode()
			rank = self.redis.get('host:%s:rank' % host).decode()
			addr = self.redis.get('host:%s:addr' % host).decode()

		if not host or not rack or not rank or not addr:
			for row in stack.api.Call('list.host', [ client ]):
				host = row['host']
				rack = row['rack']
				rank = row['rank']

			if host: 
				self.updateKey('host:%s:name' % client, host,	60 * 60)
				self.updateKey('host:%s:addr' % host,	client, 60 * 60)
				self.updateKey('host:%s:rack' % host,	rack,	60 * 60)
				self.updateKey('host:%s:rank' % host,	rank,	60 * 60)
		if host:
			return { 'name': host,
				 'addr': client,
				 'rack': rack,
				 'rank': rank }

		return None



class Processor(ProcessorBase):
	"""
	Listen for health messages and insert host:* keys into
	the redis datbase.  Keys will expire in 5 minutes.
	"""

	def channel(self):
		return 'health'

	def process(self, msg):
		keys = self.updateHostKeys(msg.getSource())

		if keys:
			self.updateKey('host:%s:status' % keys['name'],
				       msg.getMessage(),
				       60 * 2)
		return None


