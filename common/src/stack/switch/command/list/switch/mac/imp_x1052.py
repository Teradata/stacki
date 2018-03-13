# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import subprocess
from stack.exception import CommandError
from stack.switch import SwitchDellX1052, SwitchException


class Implementation(stack.commands.Implementation):
	def run(self, args):

		switch = args[0]

		# Get frontend ip for tftp address
		try:
			(_frontend, *args) = [host for host in self.owner.call('list.host.interface', ['localhost'])
					if host['network'] == switch['network']]
		except:
			raise CommandError(self, '"%s" and the frontend do not share a network' % switch['host'])

		# Send traffic through the switch first before requesting mac table
		if self.owner.pinghosts:
			_host_interfaces = [host for host in self.owner.call('list.host.interface')
					if host['network'] == switch['network']]
			for host in _host_interfaces:
				x = subprocess.Popen(['ping', '-c', '1', host['ip']], stdout=subprocess.PIPE)

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
				switch.get_mac_address_table()

				hosts = switch.parse_mac_address_table()
				for _vlan, _mac, _port, _ in hosts:
					_hostname, _interface = self.owner.db.select("""
					  n.name, nt.device from
					  nodes n, networks nt
					  where nt.node=n.id
					  and nt.mac='%s'
					""" % _mac)[0]
					self.owner.addOutput(switch_name, [_port, _mac, _hostname, _interface,  _vlan])
			except SwitchException as switch_error:
				raise CommandError(self, switch_error)
			except:
				raise CommandError(self, "There was an error getting the mac address table")
