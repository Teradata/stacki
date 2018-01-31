# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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
		_switches = self.getSwitchNames(args)
		self.beginOutput()
		for switch in self.call('list.host.interface', _switches):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']

			# Connect to switch
			with SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.get_interface_status_table()

				ports = switch.parse_interface_status_table()
				_hosts = self.getHostsForSwitch(switch_name)
				for _port,_ , _, _speed, _, _, _state, _, _ in ports:
					# if there is a host we are managing on the port, show host information
					if _port in _hosts:
						host, interface, port, vlan, mac = _hosts[_port].values()
						self.addOutput(switch_name, [_port, _speed, _state, mac,  vlan, host, interface])
					else:
						self.addOutput(switch_name, [_port, _speed, _state, '',  '', '', ''])

		self.endOutput(header=['switch', 'port',  'speed', 'state', 'mac', 'vlan', 'host', 'interface'])
