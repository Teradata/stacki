# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import stack.mq
import psutil


class Producer(stack.mq.producers.ProducerBase):
	"""
	Produces an alive message of the "health" channel
	once every 60 seconds.
	"""

	def schedule(self):
		return 60

	def produce(self):

		payload = { 'state': 'online' }

		# TODO
		#
		# Should we add some simple ganglia like metrics here (psutil
		# can do this)
		#
		# - load
		# - temp
		# - diskspace (this sucks because it's an array)

		for p in psutil.process_iter(attrs=['name']):
			if p.info['name'] == 'sshd':
				payload['ssh'] = 'up'

		return stack.mq.Message(json.dumps(payload),
					channel='health', 
					ttl=self.schedule() * 2)



