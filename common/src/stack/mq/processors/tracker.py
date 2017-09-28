# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

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


