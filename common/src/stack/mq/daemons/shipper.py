#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import sys
import socket
import threading
import signal
import daemon
import lockfile.pidlockfile
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
				self.tx.sendto(message.dumps().encode(), self.dst)
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
				self.rep.send_string('')
				c = ''
			
			if c == 'enable':
				chan = str(msg['channel'])
				if chan not in self.channels:
					subscriber.subscribe(chan)
					self.channels.append(chan)
				self.rep.send_string('Enabled channel: %s' % chan)

			elif c == 'disable':
				chan = str(msg['channel'])
				if chan in self.channels:
					if not chan == 'rmq':
						subscriber.unsubscribe(chan)
					self.channels.remove(chan)
				self.rep.send_string('Disabled channel: %s' % chan)

			elif c == 'status':
				channels = self.channels +  list(subscriber.channels.keys())
				self.rep.send_string("Enabled channels: %s" % ' '.join(channels))
			else:
				self.rep.send_string('')


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
	lock = lockfile.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' %
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


