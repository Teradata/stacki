# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.switch import SwitchDellX1052
import subprocess

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.list.command,
	      stack.commands.HostArgumentProcessor):
	pass

class Command(command):
	"""
	"""
	def run(self, params, args):

		macs = {}
		_switches = self.getSwitchNames()
		_hosts = list(set(self.getHostnames(args)).difference(_switches))
		_switches = list(self.getSwitchesForHosts(_hosts))
		self.beginOutput()
		for switch in self.call('list.host.interface', _switches):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]


			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']

			with SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.get_interface_status_table()

				# Get hosts connected to switch
				_hosts = self.getHostsForSwitch(switch_name)

				ports = switch.parse_interface_status_table()
				for _port,_ , _, _speed, _, _, _state, _, _ in ports:
					if _port in _hosts:
						host, interface, port, vlan, mac = _hosts[_port].values()
						self.addOutput(switch_name, [_port, _speed, _state, mac,  vlan, host, interface])

		self.endOutput(header=['switch', 'port',  'speed', 'state', 'mac', 'vlan', 'host', 'interface'])
