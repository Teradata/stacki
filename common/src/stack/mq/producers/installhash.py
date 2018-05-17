# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.mq
import socket
import os
import json


class Producer(stack.mq.producers.ProducerBase):
	"""
	Produces a message on the the "installhash" channel once every 60 seconds.
	The message is the contents of the /opt/stack/etc/install.hash file, which is
	the "installation hash" for this machine.
	"""

	def __init__(self, scheduler, sock):
		self.hostname = socket.gethostname()
		stack.mq.producers.ProducerBase.__init__(self, scheduler, sock)

	def schedule(self):
		return 60

	def produce(self):
		msg = {}
		if os.path.exists('/opt/stack/etc/install.hash'):
			msg['hashes'] = []
			#
			# the install.hash file should have a format like:
			#
			# 579cb47b6900f774dc36a7c381e01513  stacki
			# 0736f5c3cb54934dfc76523b3039e63d  SLES
			# 517a0ec7bce83718c684db38230347ec  profile
			#
			f = open('/opt/stack/etc/install.hash', 'r')
			for line in f.readlines():
				l = line.split()
				if len(l) == 2:
					h = {}
					h['name'] = l[1]
					h['hash'] = l[0]

					msg['hashes'].append(h)
			f.close()

		return msg

	def channel(self):
		return 'installhash'


