# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.mq.processors


class Processor(stack.mq.processors.ProcessorBase):
	"""
        Listen for install hash messages and store them in the redis database.
	"""

	def isActive(self):
		return self.redis

	def channel(self):
		return 'installhash'

	def process(self, msg):
		id = self.getKey('host:%s:id' % msg.getSource())
		if id:
			self.setKey('host:%s:installhash' % id, msg.getPayload())

		return None
