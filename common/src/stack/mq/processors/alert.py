# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import redis
import stack.mq.processors


class Processor(stack.mq.processors.ProcessorBase):
	"""
        Listen for alert messages and store them in the 
        redis database.
	"""

	def __init__(self, context, sock):
		self.redis = redis.StrictRedis()
		stack.mq.processors.ProcessorBase.__init__(self, context, sock)

	def isActive(self):
		return self.isMaster()

	def channel(self):
		return 'alert'

	def process(self, message):

		if not message.getSource():
			message.setSource('127.0.0.1')

		# Lookup the hostname of the source, if we don't find it
		# just drop the alert since we don't know about the machine.

		host = self.redis.get('host:%s:name' % message.getSource()).decode()
		if host:
			message.setSource(host)
			self.redis.rpush('alert:%s' % host, message.getMessage())

		return None


