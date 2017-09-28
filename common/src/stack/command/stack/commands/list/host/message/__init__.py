# @SI_Copyright@
#			       stacki.com
#				  v4.0
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
import signal
import zmq
import pprint
import stack.mq
import stack.commands.list.host


class Subscriber(stack.mq.Subscriber):
	def __init__(self, context, channel, host):
		stack.mq.Subscriber.__init__(self, context, host)
		self.host = host
		self.subscribe(channel)

	def callback(self, message):
		c = message.getChannel()
		i = message.getID()
		h = message.getHops()
		s = message.getSource()

		print()
		msg_info = '%s: publisher=%s' % (message.getTime(), self.host) 
		if s:
			msg_info = msg_info + ' source=%s' % s
		if c:
			msg_info = msg_info + ' channel=%s' % c
		if i:
			msg_info = msg_info + ' id=%d' % i
		if h:
			msg_info = msg_info + 'hops=%d' % h

		print(msg_info)
		p = pprint.PrettyPrinter()
		m = message.getMessage()
		try:
			o = json.loads(m)
		except:
			o = m
		p.pprint(o)



class Command(stack.commands.list.host.command):
	"""
	Attaches to one or more hosts' Message Queue and displays
	all messages on the provided channel(s).

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, listen
	to all host Message Queues.
	</arg>

	<param type='string' name='channel' optional='1'>
	Name of the channel, if not provided listen to all channels.
	</param>
	
	<example cmd='list host message backend-0-0 channel=debug'>
	Listen to the debug channel on backend-0-0
	</example>
	"""

	def handler(self, signal, frame):
		pass

	def run(self, params, args):

		(channel, ) = self.fillParams([
				('channel', '')
				])

		context = zmq.Context()
		for host in self.getHostnames(args):
			subscriber = Subscriber(context, channel, host)
			subscriber.setDaemon(True)
			subscriber.start()

		signal.signal(signal.SIGINT, self.handler)
		signal.pause()

			

