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
		for switch in self.call('list.host.interface', _switches):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']

			self.beginOutput()
			with SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.get_interface_status_table()

				hosts = switch.parse_interface_status_table()
				for _port,_ , _, _speed, _, _, _state, _, _ in hosts:
					#_hostname, _interface = self.db.select("""
					#  n.name, nt.device, nt.vlan, nt.mac from
					#  nodes n, networks nt
					#  where nt.node=n.id
					#  and nt.mac='%s'
					#""" % _mac)
					self.addOutput(switch_name, [_port, _speed, _state, '',  '', '', ''])

			self.endOutput(header=['switch', 'port',  'speed', 'state', 'mac', 'vlan', 'host', 'interface'])
