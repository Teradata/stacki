#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import sys
import daemon
import lockfile.pidlockfile
import signal
import time
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
		channel = message.getChannel()

		# For each channel keep track of the last message
		# ID and timestamp.
		#
		# Clients can ask the controller for this info
		# so they know what to subscribe to.

		if channel in self.channels:
			num = self.channels[channel]['id'] + 1
		else:
			self.channels[channel] = {}
			num = 0
		message.setID(num)
		self.channels[channel]['id']   = message.getID()
		self.channels[channel]['time'] = message.getTime()

		# Publish the message:
		#
		# <channel> stack.mq.Message
		#   text	json

		message.addHop().setChannel(None)

		if 'STACKDEBUG' in os.environ:
			print(message)
		self.pub.send_multipart((channel.encode(), str(message).encode()))

		# If this is the first message for the given channel 
		# send the list of channels over the smq channel to
		# subscribers.
		#
		# Actually we send the status on every 12th message
		# for each channel.  Heartbeat is every 5 seconds, so
		# this means at least once a minute.
		#
		# TODO: Think about how to be smarter here

		if (num % 12) == 0:
			message = stack.mq.Message({'type':'status', 'channels':self.channels},
						   time=time.asctime())
			self.pub.send_multipart(('smq'.encode(), str(message).encode()))


def Handler(signal, frame):
	sys.exit(0)


if 'STACKDEBUG' not in os.environ:
	lock = lockfile.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' % 
						('smq-publisher', 'smq-publisher'))
	daemon.DaemonContext(pidfile=lock).open()

context   = zmq.Context()
publisher = Publisher(context, stack.mq.ports.subscribe)
publisher.setDaemon(True)

publisher.start()

signal.signal(signal.SIGINT, Handler)
signal.pause()

