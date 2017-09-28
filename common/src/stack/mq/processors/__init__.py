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
import stack.mq


class ProcessorBase(stack.mq.Subscriber):
	"""
	Base class for the metric Processor.
	"""

	def __init__(self, context, sock):
		stack.mq.Subscriber.__init__(self, context)
		self.sock	= sock
		self.addr	= ('localhost', stack.mq.ports.publish)
		self.context	= context

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
				self.sock.sendto(msg.dumps(), self.addr)
		

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

