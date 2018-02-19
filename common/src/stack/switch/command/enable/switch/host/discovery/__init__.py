# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.switch import Discover, SwitchDellX1052
import subprocess

class command(stack.commands.HostArgumentProcessor,
	      stack.commands.enable.switch.host.command):
		pass

class Command(command):
	"""
	"""
	def run(self, params, args):

		hosts = self.getHostnames(args)
		_switches = self.call('list.switch', hosts)
		for switch in self.call('list.host.interface', [s['host'] for s in _switches]):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']

			x = Discover(switch_name, switch_address, frontend_tftp_address)
			x.start(self)
