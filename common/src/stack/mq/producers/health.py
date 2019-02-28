# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import stack.mq
import psutil
import subprocess
from pathlib import Path


class Producer(stack.mq.producers.ProducerBase):
	"""
	Produces an alive message of the "health" channel
	once every 60 seconds.
	"""

	def schedule(self):

		# For SLES the YaST installer has a second stage after a
		# reboot. This means all services are running even though the
		# installer is not complete. Inspect the system to see if we
		# are in that state, if so do not start the health messages
		# After this stage completes the system will reboot again and
		# the message queue will behave normally.
		#
		# For RedHat don't do anything special.

		# SLES15

		# surprise me

		# SLES12
		if Path('/var/lib/YaST2/reboot').is_file():
			return 0

		# SLES11
		out = subprocess.run(['chkconfig', 'autoyast'], 
				     stdout=subprocess.PIPE).stdout.decode()
		if out.split() == [ 'autoyast', 'on']:
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



