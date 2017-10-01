#! /opt/stack/bin/python3
#
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

import os
import sys
import daemon
import lockfile.pidlockfile
import signal
import zmq
import stack.mq


class Publisher(stack.mq.Receiver):

	def __init__(self, context, outPort):
		stack.mq.Receiver.__init__(self)

		self.channels = {}
		self.pub = context.socket(zmq.PUB)
		self.pub.bind('tcp://*:%d' % outPort)


	def callback(self, message):
		"""
		Process incomming messages from the UDP receiver.
		"""

		chan = message.getChannel()

		# For each channel keep track of the last message
		# ID and timestamp.
		#
		# Clients can ask the controller for this info
		# so they know what to subscribe to.

		if chan in self.channels:
			num  = self.channels[chan]['id'] + 1
		else:
			self.channels[chan] = {}
			num = 0
		message.setID(num)
		self.channels[chan]['id']   = message.getID()
		self.channels[chan]['time'] = message.getTime()

		# Publish the message:
		#
		# <channel> stack.mq.Message
		#   text	json

		message.addHop()

		if 'STACKDEBUG' in os.environ:
			print ("%s" % message.dumps())
		self.pub.send_multipart((message.getChannel().encode(),
			message.dumps(channel=False).encode()))

		# If this is the first message for the given channel 
		# send the list of channels over the rmq channel to
		# subscribers.
		#
		# Actually we send the status on every 12th message
		# for each channel.  Heartbeat is every 5 seconds, so
		# this means at least once a minute.
		#
		# TODO: Think about how to be smarter here

		if (num % 12) == 0:
			message = stack.mq.Message('rmq', 
					{'type'    : 'status',
					'channels': self.channels})
			self.pub.send_multipart((message.getChannel().encode(),
						 message.dumps(channel=False).encode()))


def Handler(signal, frame):
	sys.exit(0)


if 'STACKDEBUG' not in os.environ:
	lock = lockfile.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' % 
				('rmq-publisher', 'rmq-publisher'))
	daemon.DaemonContext(pidfile=lock).open()

context   = zmq.Context()
publisher = Publisher(context, stack.mq.ports.subscribe)
publisher.setDaemon(True)

publisher.start()

signal.signal(signal.SIGINT, Handler)
signal.pause()

