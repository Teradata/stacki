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

import time
import threading
import zmq
import json
import socket
import sys
import os


class ports:
	"""
	Socket port numbers used by the Stack Message Queue daemons.

	:var publish: UDP socket service for publishing a message
	:var subscribe: zmq.SUB socket for subscribing to a channel
	:var control: TCP socket service for enabling/disabling channel propagation
	"""
	publish		= 5000
	subscribe	= 5001
	control		= 5002


class Message():
	"""
	Stack Message Queue Message

	A Message is composed of header fields and the *message* text body.  For many
	applications only body is manipulated and other fields are controlled by
	lower software levels.  

	For simple Messages the *message* body can be a string.  For more complex Messages
	the body should be a json encoded python dictionary.
	"""

	def __init__(self, channel=None, message=None, hops=0, source=None, time=None, id=None):
		"""
		Constructor will create a new empty :class:`Message` add set any of the fields
		provided in the parameter list.

		:param channel: channel source or destination
		:type channel: string

		:param message: body of message
		:type message: string

		:param hops: number software hops traversed
		:type hops: int

		:param source: source host (usually an IP address)
		:type source: string

		:param time: text timestamp
		:type time: string

		:param id: unique message identifier
		:type id: int

		:returns: a new :class:`Message`
		"""
		self.channel = channel
		self.message = message
		self.hops    = hops
		self.source  = source
		self.time    = time
		self.id	     = id

	def getChannel(self):
		"""
		:returns: channel name
		"""
		return str(self.channel)

	def setChannel(self, channel):
		"""
		Set the channel name

		:param channel: channel name
		:param channel: string
		"""
		self.channel = channel

	def getMessage(self):
		"""
		:returns: message text
		"""
		return self.message

	def setMessage(self, message):
		"""
		Sets the message text
		
		:param message: text
		:type message: string
		"""
		self.message = message

	def getHops(self):
		"""
		:returns: number of software hops 
		"""
		return self.hops

	def getSource(self):
		"""
		:returns: source address
		"""
		return self.source

	def setSource(self, addr):
		"""
		Set the source host address.  This address can be a hostname
		or an IP Address.
		
		:param addr: source address
		:type addr: string
		"""
		self.source = addr

	def getTime(self):
		"""
		:returns: timestamp
		"""
		return self.time

	def setTime(self, t):
		"""
		Sets the timestamp.  Timestamps should be human readable
		and reflect the time the message was first inserted into
		the message queue.

		:param t: timestamp
		:type t: string
		"""
		self.time = t

	def getID(self):
		"""
		:returns: :class:`Message` ID
		"""
		return self.id

	def setID(self, id):
		"""
		Sets the numeric identifier.
		Identifiers must be unique for a given channel and host.

		:param id: numeric identifier
		:type id: int
		"""
		self.id = id

	def addHop(self):
		"""
		Increments the hop count for the :class:`Message`.  A hop is
		defined as a software hop not a physical network hop.  
		Every time an application receives and retransmits a message the
		hop should be incremented.  
		This value is used to debugging.
		"""
		self.hops += 1

	def getDict(self, channel=True):
		"""
		Returns a dictionary of all the :class:`Message` fields.
		By default this will include the name of the message
		channel which is correct for most uses.
		However, when the message is going to be published on a
		zeromq pub/sub socket the channel name is already prepended to
		the string containing the message.
		For this case set the *channel* parameter to False.

		:param channel: include channel field
		:type channel: bool
		:returns: python dictionary
		"""
		d = {}
		if channel:
			if self.channel:
				d['channel'] = self.channel
		if self.id is not None:
			d['id'] = self.id
		if self.message:
			d['message'] = self.message
		if self.hops:
			d['hops'] = self.hops
		if self.source:
			d['source'] = self.source
		if self.time:
			d['time'] = self.time
		return d

	def dumps(self, channel=True):
		"""
		Creates a dictionary of all the :class:`Message` fields and returns
		it as a json string. 
		Just as with :func:`getDict` the name of the message channel
		can by excluded from the resulting dictionary.

		:param channel: include channel field
		:type channel: bool
		:returns: json representation of the message
		"""
		d = self.getDict(channel)
		return json.dumps(d)

	def loads(self, packet):
		"""
		Parses the *packet* and update all the included
		message fields for this :class:`Message`.

		:param packet: json representation of a message
		:type packet: string
		"""
		d = json.loads(packet.decode())
		if 'channel' in d:
			self.channel = d['channel']
		if 'id' in d:
			self.id      = d['id']
		if 'message' in d:
			self.message = d['message']
		if 'hops' in d:
			self.hops    = d['hops']
		if 'source' in d:
			self.source  = d['source']
		if 'time' in d:
			self.time    = d['time']


class Subscriber(threading.Thread):
	"""
	A Subscriber thread is used by application to subscribe and unsubscribe
	to channels on a message queue on exactly one host.
	For every :class:`Message` received a :func:`callback` is invoked and the
	message is handled according to the derived class implementation.
	Once the subscribe thread is started it will not exit.
	"""

	def __init__(self, context, host='localhost'):
		"""
		Constructor creates a new :class:`Subscriber` and connects to the
		zeromq subcribe socket on the remote *host*.

		:param context: zeromq context
		:param host: name of publishing host
		:type host: string

		:returns: a new :class:`Subscriber`
		"""
		threading.Thread.__init__(self)

		self.sub = context.socket(zmq.SUB)
		self.sub.connect('tcp://%s:%d' % (host, ports.subscribe))

	def subscribe(self, channel):
		"""
		Subscribes to all channels that start with the
		sub-string *channel*.

		:param channel: pattern of channels to subscribe
		:type channel: string
		"""
		self.sub.setsockopt_string(zmq.SUBSCRIBE, channel)

	def unsubscribe(self, channel):
		"""
		Unsubscribe from the given *channel*.  Subscriptions are
		reference counted so you must unsubscribe once for every
		time you :func:`subscribe`.

		:param channel: channel name
		:type channel: string
		"""
		self.sub.setsockopt_string(zmq.UNSUBSCRIBE, channel)
		
	def run(self):
		while True:
			try:
				channel, pkt = self.sub.recv_multipart()
				msg = Message(channel)
				msg.loads(pkt)
			except:
				continue
			if 'STACKDEBUG' in os.environ:
				print (msg.getDict())
			self.callback(msg)


	def callback(self, message):
		"""
		Called for every received message.  All derived classes must
		implement this method.  The default behavior does nothing.

		:param message: received message
		:type message: stack.mq.Message
		"""
		pass


class Receiver(threading.Thread):
	"""
	A Receiver thread listens on a UDP socket and receives both
	text messages and :class:`Message` objects.
	For every message received a :func:`callback` is invoked and the
	message is handled according to the derived class implementation.
	Once the Receiver thread is started it will not exit.
	"""

	def __init__(self):
		threading.Thread.__init__(self)

		self.rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.rx.bind(('', ports.publish))

	def run(self):
		while True:
			pkt, addr = self.rx.recvfrom(65565)

			# All clients send text (<channel> <message>)
			# But, internally all messages are json.  To allow
			# arbitrary wiring of daemons we need to accept
			# json as input also.
			#
			# Note the callback() always pushes data as
			# stack.mq.Message objects.  This is the only
			# part of the code where we handle receiving 
			# unstructured data.
			#
			# Design point here was to keep the clients 
			# simple so we don't need an API to write to
			# the message queue.

			msg = None
			tm  = time.asctime()
			try:
				msg = Message(time=tm)
				msg.loads(pkt)
			except:
				try:
					(c, m) = pkt.split(' ', 1)
					msg = Message(c, m, time=tm)
				except:
					pass # drop bad message
			if msg:
				if not msg.getSource() and addr[0] != '127.0.0.1':
					msg.setSource(addr[0])
				self.callback(msg)

	def callback(self, message):
		"""
		Called for every received message.  All derived classes must
		implement this method.  The default behavior does nothing.

		:param message: received message
		:type message: stack.mq.Message
		"""
		pass






