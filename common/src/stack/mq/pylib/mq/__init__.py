# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import time
import threading
import json
import socket
import sys
import os

# We need the "ports" class when we are inside the installer, but don't need to
# setup and zmq based services. The alternative is to add zmq and dependencies
# to the installer. Both solutions are ugly, but this on follows who we treat
# the command line and allow it to be in the installer without the database.

try:
	import zmq
except ImportError:
	pass



class ports:
	"""
	Socket port numbers used by the Stack Message Queue daemons.

	:var publish: UDP socket service for publishing a message
	:var subscribe: zmq.SUB socket for subscribing to a channel
	:var control: TCP socket service for enabling/disabling channel propagation
	"""
	publish	  = 5000
	subscribe = 5001
	control	  = 5002


class Message():
	"""
	Stack Message Queue Message

	A Message is composed of header fields and the *message* text body.  For many
	applications only body is manipulated and other fields are controlled by
	lower software levels.  

	For simple Messages the *message* body can be a string.  For more complex Messages
	the body should be a json encoded python dictionary.
	"""

	def __init__(self, payload=None, *, message=None, channel=None, hops=None, ttl=None, source=None, time=None, id=None):
		"""
		Constructor will create a new empty :class:`Message` add set any of the fields
		provided in the parameter list.

		:param payload: body of message
		:type payload: string

		:param message: json representation of a Message
		:type message: string

		:param channel: channel source or destination
		:type channel: string

		:param hops: number software hops traversed
		:type hops: int

		:param ttl: time to live for message
		:type ttl: int

		:param source: source host (usually an IP address)
		:type source: string

		:param time: text timestamp
		:type time: string

		:param id: unique message identifier
		:type id: int

		:returns: a new :class:`Message`
		"""

		if message:
			msg = json.loads(message)
		else:
			msg = {}

		# JSON does not override parameters, this allows loading an
		# existing Message and overwriting some of the fields
		
		self.channel = channel if channel else msg.get('channel')
		self.id      = id      if id      else msg.get('id')
		self.payload = payload if payload else msg.get('payload')
		self.hops    = hops    if hops    else msg.get('hops')
		self.ttl     = ttl     if ttl     else msg.get('ttl')
		self.source  = source  if source  else msg.get('source')
		self.time    = time    if time    else msg.get('time')

		# Set default values for hops and ttl

		if self.hops is None:
			self.hops = 0
		if self.ttl is None:
			self.ttl  = 30

	def __str__(self):
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
		if self.channel is not None:
			d['channel'] = self.channel
		if self.id is not None:
			d['id'] = self.id
		if self.payload:
			d['payload'] = self.payload
		if self.hops:
			d['hops'] = self.hops
		if self.ttl:
			d['ttl'] = self.ttl
		if self.source:
			d['source'] = self.source
		if self.time:
			d['time'] = self.time
		return json.dumps(d)


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
		return self

	def getPayload(self):
		"""
		:returns: payload text
		"""
		return self.payload

	def setPayload(self, payload):
		"""
		Sets the payload text
		
		:param payload: text
		:type payload: string
		"""
		self.payload = payload
		return self

	def getHops(self):
		"""
		:returns: number of software hops 
		"""
		return self.hops

	def getTTL(self):
		"""
		:returns: time to live
		"""
		return self.ttl

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
		return self

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
		return self

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
		return self

	def addHop(self):
		"""
		Increments the hop count for the :class:`Message`.  A hop is
		defined as a software hop not a physical network hop.  
		Every time an application receives and retransmits a message the
		hop should be incremented.  
		This value is used to debugging.
		"""
		self.hops += 1
		return self



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
				channel, payload = self.sub.recv_multipart()
				msg = Message(message=payload.decode(), 
					      channel=channel.decode())
			except:
				continue
			if 'STACKDEBUG' in os.environ:
				print(msg)
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

			# All clients send text (<channel> <payload>)
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
			try:		      # try json first
				msg = Message(message=pkt.decode())
			except:
				try:
					(channel, payload) = pkt.decode().split(' ', 1)
					msg = Message(payload, channel=channel)
				except:
					pass   # drop bad message
			if msg:
				if not msg.getTime():
					msg.setTime(time.asctime())
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






