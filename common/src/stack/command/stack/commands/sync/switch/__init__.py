# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
import stack.switch
import subprocess

class command(stack.commands.HostArgumentProcessor,
	stack.commands.sync.command):
		pass

class Command(command):
	"""
	Uploads config file to switch
	"""
	def run(self, params, args):

		hosts = self.getHostnames(args)
		frontend, *xargs = self.db.getHostname('localhost')
		switches = self.call('list.switch', hosts)
		for switch in self.call('list.host.interface', [s['host'] for s in switches]):

			# Get frontend ip for tftp address
			(frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
				if host['network'] == switch['network']]	
			frontend_tftp_address = frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']
			with stack.switch.SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as _switch:
				_switch.set_tftp_ip(frontend_tftp_address)
				_switch.set_filenames(switch_name)
				_switch.connect()
				_switch.upload()
