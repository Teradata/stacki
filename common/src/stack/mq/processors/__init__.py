# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
from stack.topo import Redis
import stack.mq
try:
	import redis
except ModuleNotFoundError:
	pass



class ProcessorBase(stack.mq.Subscriber):
	"""
	Base class for the metric Processor.
	"""

	def __init__(self, context, sock):
		stack.mq.Subscriber.__init__(self, context)
		self.sock	= sock
		self.addr	= ('localhost', stack.mq.ports.publish)
		self.context	= context

		try:
			self.redis = redis.StrictRedis(host=Redis.server)
		except NameError:
			self.redis = None


	def getKey(self, key):
		try:
			value = self.redis.get(key)
		except redis.exceptions.ConnectionError:
			return None

		if value is not None:
			return value.decode()
		return None

	def setKey(self, key, value, ttl=None):
		try:
			self.redis.set(key, value)
		except redis.exceptions.ConnectionError:
			return

		if ttl is not None:
			self.redis.expire(key, ttl)


	def run(self):
		if self.isActive():
			self.subscribe(self.channel())
			stack.mq.Subscriber.run(self)

	def callback(self, message):
		o = []
		if 'STACKDEBUG' not in os.environ:
			try:
				o = self.process(message)
			except:
				pass
		else:
			o = self.process(message)

		if isinstance(o, list):
			msgs = o
		else:
			msgs = [ o ]

		for msg in msgs:
			if msg:
				self.sock.sendto(str(msg), self.addr)
		

	def process(self, message):
		"""
		Callback to process a newly received message.  
		Returns a message to be inserted back into the 
		message queue of None if no action is to be taken.

		:returns: new Message or None
		"""
		return None

	def channel(self):
		"""
		Return the name of the channel that this processor
		operates on.  All derived classes must implement this
		method.
		
		:returns: subscription channel name
		"""
		return None

	
	def isMaster(self):
		"""
		Return True if this is the master host in the message
		queue.

		:returns: boolean value
		"""
		return not os.path.exists('/etc/sysconfig/stack-mq')

	def isActive(self):
		"""
		Returns True if the Processor should be run.  This allows
		a common set of Processors to be deployed on different
		hosts and have each host decide if it should be used.

		The default is True.

		:returns: boolean value
		"""
		return True

