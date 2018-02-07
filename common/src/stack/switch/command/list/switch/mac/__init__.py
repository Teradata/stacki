# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
from stack.switch import SwitchDellX1052
import subprocess
from stack.exception import CommandError

class command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.list.command,
	      stack.commands.HostArgumentProcessor):
	pass

class Command(command):
	"""
	List mac address table on switch.

	<arg optional='1' type='string' name='switch' repeat='1'>
	Zero, one or more switch names. If no switch names are supplies, info about
	all the known switches is listed.
	</arg>

	<param optional='1' type='bool' name='pinghosts'>
	Send a ping to each host connected to the switch. Hosts do not show up in the
	mac address table if there is no traffic.
	</param>

	<example cmd='list host mac switch-0-0'>
	List mac table for switch-0-0.
	</example>

	<example cmd='list switch mac'>
	List mac table for all known switches/
	</example>
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
			try:
				(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost'])
						if host['network'] == switch['network']]
			except:
				raise CommandError(self, '"%s" and the frontend do not share a network' % switch['host'])

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
