# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import stack.api
import stack.mq.processors


class ProcessorBase(stack.mq.processors.ProcessorBase):
	"""
	Extends the stack.mq.processors.ProcessorBase to
	add support for creating Redis keys.  
	This is used to cache host information.
	"""

	def isActive(self):
		return self.redis

	def updateHostKeys(self, client):
		"""
		Updates the Redis keys for a given host in the cluster.	 
		If Redis does not know about the host the cluster database is inspected and
		the keys are created with a one hour timeout.
		If Redis already contains the keys the timeout is reset.
		The following Redis keys are defined for the host::

			host:ID:rack
			host:ID:rank
			host:ID:addr
			host:IPADDRESS:id

		:param addr: IP address
		:type addr: string
		:returns: dictionary with *id*, *addr*, *rack*, and *rank*
		"""
		keys = None

		if not client:
			client = '127.0.0.1'

		id = self.getKey('host:%s:id' % client)
		if id:
			rack = self.getKey('host:%s:rack' % id)
			rank = self.getKey('host:%s:rank' % id)
			addr = self.getKey('host:%s:addr' % id)

		if not id or not rack or not rank or not addr:
			for row in stack.api.Call('list.host', [ client, 'expanded=true' ]):
				id   = row['id']
				rack = row['rack']
				rank = row['rank']

				self.setKey('host:%s:id'   % client, id,     60 * 60)
				self.setKey('host:%s:addr' % id,     client, 60 * 60)
				self.setKey('host:%s:rack' % id,     rack,   60 * 60)
				self.setKey('host:%s:rank' % id,     rank,   60 * 60)
		if id:
			keys = { 'id'  : id,
				 'addr': client,
				 'rack': rack,
				 'rank': rank }

		return keys



class Processor(ProcessorBase):
	"""
	Listen for health messages and insert host:* keys into
	the redis datbase.  Keys will expire in 5 minutes.
	"""

	def channel(self):
		return 'health'

	def process(self, msg):
		keys    = self.updateHostKeys(msg.getSource())
		payload = msg.getPayload()
		ttl     = msg.getTTL()

		if keys and payload:

			# health payloads were originally just strings, but
			# this channel is going to be used to monitor more
			# stuff (e.g. is the Teradata Database up?). But for
			# now support both old style strings and a new json
			# format for the payload.
			#
			# The new format is a dictionary of component X health
			# with the following builtin components (others come
			# from pluggins).
			#
			# basic: this is the current health string
			# ssh  : is sshd running?

			try:
				health = json.loads(payload)
			except ValueError:
				health = { 'state': payload }

			for component, state in health.items():
				if ttl == -1:
					ttl = None
				self.setKey('host:%s:status:%s' % 
					    (keys['id'], component), state, ttl)


		return None


