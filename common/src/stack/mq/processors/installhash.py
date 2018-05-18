# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import redis
import stack.mq.processors


class Processor(stack.mq.processors.ProcessorBase):
	"""
        Listen for install hash messages and store them in the redis database.
	"""

	def __init__(self, context, sock):
		self.redis = redis.StrictRedis()
		stack.mq.processors.ProcessorBase.__init__(self, context, sock)

	def isActive(self):
		return self.isMaster()

	def channel(self):
		return 'installhash'

	def process(self, msg):
		# Lookup the hostname of the source, if we don't find it
		# just drop the message since we don't know about the machine.
		host = self.redis.get('host:%s:name' % msg.getSource())
		if host:
			host = host.decode()
			msg.setSource(host)
			self.redis.set('host:%s:installhash' % host, msg.getMessage())

		return None
