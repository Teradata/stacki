# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import json
import stack.mq


class ProducerBase:
	"""
	Base class for the metric Producer.
	"""

	def __init__(self, scheduler, sock):
		"""
		:param scheduler: timer based scheduling object
		:param sock: publishing socket
		"""
		self.scheduler	= scheduler
		self.sock	= sock
		self.addr	= ('localhost', stack.mq.ports.publish)

	def run(self):
		"""
		Produce the next message(s) and send it to the smq-publisher UDP
		socket.  Then schedule() the next production.
		"""

		o = None
		if 'STACKDEBUG' not in os.environ:
			try:
				o = self.produce()
			except:
				pass
		else:
			o = self.produce()

		if isinstance(o, list):
			messages = o
		else:
			messages = [ o ]

		for message in messages:
			if message:
				if 'STACKDEBUG' in os.environ:
					print(message)
				self.sock.sendto(str(message).encode(),
						 self.addr)

		if self.schedule():
			self.scheduler.enter(self.schedule(), 0, self.run, ())
		
		
	def schedule(self):
		"""
		How soon should the next produce() happen in
		seconds.  Default is every minute.
		"""
		return 60

	def produce(self):
		"""
		Produce another metric, the result must be Message
		or list of Messages.

		:returns: Message(s)
		"""
		return None


