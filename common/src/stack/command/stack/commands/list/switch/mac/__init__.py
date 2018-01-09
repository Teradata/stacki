# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.util
import stack.switch
import subprocess

def confirm_hosts(macs, line):
	if 'dynamic' in line:
		(_vlan, _mac, _port, _) = line.split()
		_switch_port = _port.split('/')[-1]
		if _mac in macs:
			_host = macs[_mac]['host']
			_interface = macs[_mac]['interface']
			_host_port = macs[_mac]['port']
			if _host_port == _switch_port:
				print("%s is connected to port %s with %s" % (_host, _host_port, _interface))
			else:
				print("%s is NOT connected to port %s with %s" % (_host, _host_port, _interface))
		else:
				print("No machine is connected toswitch port %s" % _switch_port)
	

class command(stack.commands.HostArgumentProcessor,
	stack.commands.list.command):
	pass

class Command(command):
	"""
	"""
	def run(self, params, args):

		(pinghosts,confirmhosts) = self.fillParams([
		('pinghosts', False),
		('confirmhosts', False),
		])

		pinghosts = self.str2bool(pinghosts)
		confirmhosts = self.str2bool(confirmhosts)

		macs = {}
		hosts = self.getHostnames(args)
		_switches = self.call('list.switch', hosts)
		for switch in self.call('list.host.interface', [s['host'] for s in _switches]):

			# Get frontend ip for tftp address
			(_frontend, *args) = [host for host in self.call('list.host.interface', ['localhost']) 
					if host['network'] == switch['network']]

			# Send traffic through the switch first before requesting mac table
			if pinghosts or confirmhosts:
				_host_interfaces = [host for host in self.call('list.host.interface', hosts)
						if host['network'] == switch['network']]

			if pinghosts:
				for host in _host_interfaces:
					x = subprocess.Popen(['ping', '-c', '1', host['ip']], stdout=subprocess.PIPE)

			if confirmhosts:
				_hosts = {}
				for host in self.call('list.host', hosts):
						_hosts[host['host']] = host

				for host in _host_interfaces:
					if host['mac']:
						macs[host['mac']] = {
							'port': _hosts[host['host']]['rank'],
							'host': host['host'],
							'interface': host['interface']
						}

			frontend_tftp_address = _frontend['ip']
			switch_address = switch['ip']
			with stack.switch.SwitchDellX1052(switch_address, 'admin', 'admin') as switch:
				switch.set_tftp_ip(frontend_tftp_address)
				switch.connect()
				switch.get_mac_address_table()
				
				with open('/tmp/mac-address-table', 'r') as f:
					lines = f.readlines()
					for line in lines:
						if confirmhosts:
							confirm_hosts(macs, line)
						else:
							print(line, end='')

				print("switch config still WIP")
