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

		(pinghosts,) = self.fillParams([
		('pinghosts', False),
		])

		pinghosts = self.str2bool(pinghosts)

		macs = {}
		_switches = self.getSwitchNames(args)
		self.beginOutput()
		for switch in self.call('list.host.interface', _switches):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			# Send traffic through the switch first before requesting mac table
			if pinghosts:
				_host_interfaces = [host for host in self.call('list.host.interface')
						if host['network'] == switch['network']]
				for host in _host_interfaces:
					x = subprocess.Popen(['ping', '-c', '1', host['ip']], stdout=subprocess.PIPE)

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			switch_name = switch['host']

			with SwitchDellX1052(switch_address, switch_name, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.get_mac_address_table()

				hosts = switch.parse_mac_address_table()
				for _vlan, _mac, _port, _ in hosts:
					_hostname, _interface = self.db.select("""
					  n.name, nt.device from
					  nodes n, networks nt
					  where nt.node=n.id
					  and nt.mac='%s'
					""" % _mac)[0]
					self.addOutput(switch_name, [_port, _mac, _hostname, _interface,  _vlan])

		self.endOutput(header=['switch', 'port',  'mac', 'host', 'interface', 'vlan'])
