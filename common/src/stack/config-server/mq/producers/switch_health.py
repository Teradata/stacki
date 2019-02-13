# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import subprocess
import stack.mq
import stack.api
import stack.api.get
from stack.switch.m7800 import SwitchMellanoxM7800
from stack.switch.x1052 import SwitchDellX1052

class Producer(stack.mq.producers.ProducerBase):
	"""
	Produces a list of health messages for every ethernet and InfiniBand switch in
	the system.
	This must run on the frontend and "spoof" the IP address of the switches because
	we can't put message queue code on the switches.
	"""

	def schedule(self):
		return 60

	def ping(self, ip):
		r = subprocess.Popen(['ping', '-c 1', '-W 1', ip], stdout=subprocess.PIPE)
		r.communicate()

		if r.returncode == 0:
			return 'online'

		return None

	def getSwitches(self):
		switches = []
		for o in stack.api.Call('list.host.interface', [ 'a:switch' ]):
			if 'default' in o and o['default']:
				switches.append(o['ip'])
		
		return switches

	def getStatus(self, switch, make, model):
		s = None
		status = None
		u = stack.api.get.GetHostAttr(switch, 'switch_username')
		p = stack.api.get.GetHostAttr(switch, 'switch_password')

		if (make, model) == ('Mellanox', 'm7800'):
			s = SwitchMellanoxM7800(switch, username = u, password = p)
		elif (make, model) == ('DELL', 'x1052'):
			s = SwitchDellX1052(switch, username = u, password = p)

		if s:
			try:
				s.connect()
				status = 'up'
			except:
				pass

		return status

	def produce(self):
		msgs = []

		for switch in self.getSwitches():
			online_status = self.ping(switch)

			ssh_status = None
			make = stack.api.get.GetHostAttr(switch, 'component.make')
			model = stack.api.get.GetHostAttr(switch, 'component.model')

			ssh_status = self.getStatus(switch, make, model)

			payload = { 'state': online_status }
			payload['ssh'] = ssh_status

			msgs.append(stack.mq.Message(json.dumps(payload), channel='health',
				source=switch, ttl=self.schedule() * 2))

		return msgs
