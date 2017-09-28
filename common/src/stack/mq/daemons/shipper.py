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
import socket
import threading
import signal
import daemon
import daemon.pidlockfile
import zmq
import json
import stack.mq


class Subscriber(stack.mq.Subscriber):
	def __init__(self, context, host):

		addr = socket.gethostbyname(host)
			
		stack.mq.Subscriber.__init__(self, context)

		self.channels = {}
		self.tx  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.dst = (addr, stack.mq.ports.publish)

	def callback(self, message):
		if message.getChannel() == 'rmq':
			rmq = message.getMessage()
			try:
				r = json.loads(rmq)
				if r['type'] == 'status':
					self.channels = r['channels']
			except:
				pass
		else:
			message.addHop()
			try:
				self.tx.sendto(message.dumps(), 
					self.dst)
			except: # ignore failed sends
				pass


class Controller(threading.Thread):
	def __init__(self, context, channels):
		threading.Thread.__init__(self)
		
		self.channels = channels
		self.rep = context.socket(zmq.REP)
		self.rep.bind('tcp://*:%d' % stack.mq.ports.control)

	def run(self):

		# Enable the default channel subscriptions

		for chan in self.channels:
			subscriber.subscribe(chan)
			
		# Subscribe to the internal channel.  This
		# does not go into the self.channels list
		# to hide from the user.

		subscriber.subscribe('rmq')

		while True:

			pkt = self.rep.recv()
			try:
				msg = json.loads(pkt)
				c = msg['command']
			except:
				self.rep.send('')
				c = ''
			
			if c == 'enable':
				chan = str(msg['channel'])
				if chan not in self.channels:
					subscriber.subscribe(chan)
					self.channels.append(chan)
				self.rep.send('')

			elif c == 'disable':
				chan = str(msg['channel'])
				if chan in self.channels:
					if not chan == 'rmq':
						subscriber.unsubscribe(chan)
					self.channels.remove(chan)
				self.rep.send('')

			elif c == 'status':
				self.rep.send(json.dumps([self.channels, 
							  subscriber.channels]))
			else:
				self.rep.send('')


def Handler(signal, frame):
	sys.exit(0)


host = None
try:
	fin = open('/etc/sysconfig/stack-mq', 'r')
	for line in fin:
		(key, val) = line[:-1].split('=', 1)
		host = val
	fin.close()
except:
	print('error - /etc/sysconfig/stack-mq bad format')
	sys.exit(-1)

channels = [  ]
try:
	fin = open('/etc/sysconfig/stack-mq-channels', 'r')
	for line in fin:
		channels.append(line.strip())
	fin.close()
except:
	print('error - /etc/sysconfig/stack-mq-channels bad format')
	sys.exit(-1)


if 'STACKDEBUG' not in os.environ:
	lock = daemon.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' % 
					('rmq-shipper', 'rmq-shipper'))
	daemon.DaemonContext(pidfile=lock).open()


context    = zmq.Context()
subscriber = Subscriber(context, host)
controller = Controller(context, channels)
subscriber.setDaemon(True)
controller.setDaemon(True)

subscriber.start()
controller.start()

signal.signal(signal.SIGINT, Handler)
signal.pause()


