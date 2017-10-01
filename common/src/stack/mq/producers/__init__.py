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
		Produce the next message(s) and send it to the rmq-publisher UDP
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
			msgs = o
		else:
			msgs = [ o ]

		for msg in msgs:
			if msg and self.channel():
				m = { "channel": self.channel(), 
					"message": msg }
				if 'STACKDEBUG' in os.environ:
					print(m)
				self.sock.sendto(json.dumps(m).encode(), self.addr)
		self.scheduler.enter(self.schedule(), 0, self.run, ())
		
		
	def schedule(self):
		"""
		How soon should the next produce() happen in
		seconds.  Default is every minute.
		"""
		return 60

	def produce(self):
		"""
		Produce another metric, the result must be a single
		string, or a list.  In the former a single message
		is produced, in the latter multiple messages are
		produced.

		:returns: Message(s)
		"""
		return None

	def channel(self):
		"""
		:returns: publisher channel name
		"""
		return None

