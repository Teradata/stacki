# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import stack.mq
import psutil
from pathlib import Path


class Producer(stack.mq.producers.ProducerBase):
	"""
	Produces an alive message of the "health" channel
	once every 60 seconds.
	"""

	def schedule(self):
		# The second stage of YaST brings up the MQ but
		# isn't really ready to start reporting infomation.
		if Path('/var/lib/YaST2/reboot').is_file():
			return 0
		return 60

	def produce(self):

		payload = { 'state': 'online' }

		# TODO
		#
		# Should we add some simple ganglia like metrics here (psutil
		# can do this)
		#
		# - load
		# - temp
		# - diskspace (this sucks because it's an array)

		for p in psutil.process_iter(attrs=['name']):
			if p.info['name'] == 'sshd':
				payload['ssh'] = 'up'

		return stack.mq.Message(json.dumps(payload),
					channel='health', 
					ttl=self.schedule() * 2)



