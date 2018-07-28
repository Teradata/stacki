# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.mq
import socket
import psutil


class Producer(stack.mq.producers.ProducerBase):
	"""
	Produces an alive message of the "health" channel
	once every 60 seconds.
	"""

	def schedule(self):
		return 60

	def produce(self):

		ssh = False
		for p in psutil.process_iter(attrs=['name']):
			if p.info['name'] == 'sshd':
				ssh = True

		if ssh:
			return stack.mq.Message('up', 
						channel='health', 
						ttl=self.schedule()*2)
		else:
			return None



