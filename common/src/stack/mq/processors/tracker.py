# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import redis
import stack.mq.processors.health

class ProcessorBase(stack.mq.processors.health.ProcessorBase):
	"""
	Further extends the ProcessorBase for processing Avalanche
	tracker (and HDFS) messages indended for Arbor.js consumption.
	Received Messages are json dictionaries to *from* and *to*
	fields set to IP Addresses.
	The processor uses the Redis database to convert these fields
	to hostname and also add the *rack* and *rank* for the corresponding
	hosts.
	"""

	def fieldCallback(self, field, keys):
		"""
		Derived classes may optionally implement to have a 
		callback for every *from* and *to* host in
		the received messages.
		The callback will receive the new dictionary with the
		full hostname, rack, and rank.

		:param keys: dictionary of *host*, *rack*, *rank*
		:type: dict
		"""
		pass

	def process(self, message):

		if self.channel().find('raw') == 0:
			message.setChannel(self.channel()[3:])
		message.addHop()

		dict = json.loads(message.getMessage())
		for field in [ 'from', 'to' ]:

			keys = self.updateHostKeys(dict[field])

			if keys['addr'] == '127.0.0.1':
				name = 'frontend-0-0'
			else:
				name = keys['name']

			dict[field] = { 'host': name,
					'rack': keys['rack'],
					'rank': keys['rank'] }

			self.fieldCallback(field, keys)

		message.setMessage(json.dumps(dict))

		return message



class Processor(ProcessorBase):

	def channel(self):
		return 'rawtracker'

	def fieldCallback(self, field, keys):
		"""
		For the destination host update the status to 
		'installing'.  This is not done for the source
		host since it may be the Frontend and is not
		actually installing.
		"""
		if field == 'to':
			self.updateKey('host:%s:status' % keys['name'], 
				       'installing', 60*60)


