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

	def schedule(self):
		return 60

	def produce(self):
		message = None

		# the install.hash file should have a format like:
		#
		# 579cb47b6900f774dc36a7c381e01513  stacki
		# 0736f5c3cb54934dfc76523b3039e63d  SLES
		# 517a0ec7bce83718c684db38230347ec  profile

		if os.path.exists('/opt/stack/etc/install.hash'):
			payload = [ ]
			with open('/opt/stack/etc/install.hash', 'r') as f:
				for line in f.readlines():
					l = line.split()
					if len(l) == 2:
						payload.append({'name': l[1],
								'hash': l[0]})
			if payload:
				message = stack.mq.Message(payload,
							   channel='installhash')

		return message



