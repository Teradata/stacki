# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from operator import itemgetter

import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'ib_subnetmanager'

	def requires(self):
		return ['basic']

	def run(self, hosts):
		if not self.owner.expanded:
			return {'keys': [], 'values': {}}

		switch_attrs = self.owner.getHostAttrDict('a:switch')

		host_info = dict.fromkeys(hosts)
		for host in dict(host_info):
			make, model = (switch_attrs[host].get('component.make'), switch_attrs[host].get('component.model'))
			if (make, model) != ('Mellanox', 'm7800'):
				# ... but set other hosts to an empty value instead of False
				host_info[host] = (None,)
				continue

			kwargs = {
				'username': switch_attrs[host].get('username'),
				'password': switch_attrs[host].get('password'),
			}

			# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
			kwargs = {k:v for k, v in kwargs.items() if v is not None}

			s = SwitchMellanoxM7800(host, **kwargs)
			s.connect()
			host_info[host] = (s.subnet_manager,)

		return { 'keys' : [ 'ib subnet manager', ],
			'values': host_info }

