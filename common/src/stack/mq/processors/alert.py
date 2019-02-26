# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.mq.processors


class Processor(stack.mq.processors.ProcessorBase):
	"""
        Listen for alert messages and store them in the 
        redis database.
	"""

	def isActive(self):
		return self.redis

	def channel(self):
		return 'alert'

	def process(self, message):
		if not message.getSource():
			message.setSource('127.0.0.1')

		self.redis.rpush('alert:%s' % message.getSource(), 
				 message.getPayload())

		return None


