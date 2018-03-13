# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchDellX1052, SwitchException


class Implementation(stack.commands.Implementation):
	def run(self, args):

		switch = args[0]
		hostnames= self.owner.hosts

		# Get frontend ip for tftp address
		try:
			(_frontend, *args) = [host for host in self.owner.call('list.host.interface', ['localhost'])
					if host['network'] == switch['network']]
		except:
			raise CommandError(self, '"%s" and the frontend do not share a network' % switch['host'])

		frontend_tftp_address = _frontend['ip']
		switch_address = switch['ip']
		switch_name = switch['host']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')

		# Connect to the switch
		with SwitchDellX1052(switch_address, switch_name, switch_username, switch_password) as switch:
			try:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.get_interface_status_table()

				# Get hosts connected to switch
				_hosts = {}
				hosts = self.owner.getHostsForSwitch(switch_name)
				for port in dict(hosts):
					if hosts[port]['host'] in hostnames:
						_hosts[port] = dict(hosts[port])

				ports = switch.parse_interface_status_table()
				for _port,_ , _, _speed, _, _, _state, _, _ in ports:
					if _port in _hosts:
						host, interface, port, vlan, mac = _hosts[_port].values()
						self.owner.addOutput(host, [mac, interface, vlan, switch_name,  _port, _speed, _state])
			except SwitchException as switch_error:
				raise CommandError(self, switch_error)
			except:
				raise CommandError(self, "There was an error getting the status of the switch.")
