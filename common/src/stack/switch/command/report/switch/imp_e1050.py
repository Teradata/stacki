# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import ipaddress
import re
import stack.commands
from stack.exception import CommandError
from stack.switch.e1050 import SwitchCelesticaE1050
import subprocess


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch = args[0]

		self.switch_name = switch['switch']
		switch_interface = [interface for interface in self.owner.call('list.host.interface', [self.switch_name])
				    if interface['default']][0]
		self.switch_address = switch_interface['ip']
		switch_username = self.owner.getHostAttr(self.switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(self.switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, self.switch_name, switch_username, switch_password)

		self.switch_network = self.owner.call('list.network', [switch_interface['network']])[0]
		self.networks = {self.switch_network['network']: self.switch_network}

		# Get frontend ip
		try:
			self.frontend, *_ = [iface for iface in self.owner.call('list.host.interface', ['localhost'])
				if iface['network'] == switch_interface['network']]
		except:
			raise CommandError(self, f'{self.self.switch_name} and the frontend do not share a network')

		self.owner.addOutput('localhost', f'<stack:file stack:name="/tmp/{self.switch_name}/new_config">')
		self.reset()
		self.sync_config()
		self.owner.addOutput('localhost', '</stack:file>')

	def reset(self):
		switch_interface = ipaddress.IPv4Interface(f"{self.switch_network['gateway']}/{self.switch_network['mask']}")
		swps = self.get_swp_range()

		commands = [
			'del all',
			'add routing log syslog informational',
			'add snmp-server listening-address localhost',
			f'add bridge bridge ports swp{swps}',
			'add bridge bridge pvid 1',
			'add bridge bridge vids 1',
			'add bridge bridge vlan-aware',
			'add bridge pre-up sysctl -w net.ipv4.conf.all.proxy_arp=1',
			'add bridge pre-up sysctl -w net.ipv4.conf.default.proxy_arp=1',
			'add interface eth0',# ip address dhcp',
			'add loopback lo',# ip address 127.0.0.1/32',
			'add time zone Etc/UTC',
			'add time ntp server 0.cumulusnetworks.pool.ntp.org iburst',
			'add time ntp server 1.cumulusnetworks.pool.ntp.org iburst',
			'add time ntp server 2.cumulusnetworks.pool.ntp.org iburst',
			'add time ntp server 3.cumulusnetworks.pool.ntp.org iburst',
			'add time ntp source eth0',
			'add dot1x radius accounting-port 1813',
			'add dot1x eap-reauth-period 0',
			'add dot1x radius authentication-port 1812',
			'add dot1x mab-activation-delay 30',
			f'add vlan 1 ip address {switch_interface.with_prefixlen}',
			f'add hostname {self.switch_name}',
			]

		for command in commands:
			self.owner.addOutput('localhost', command)

	def sync_config(self):
		mac_ifaces = {iface['mac']: iface for iface in self.owner.call('list.switch.host', [self.switch_name])}
		hosts = [iface['host'] for iface in mac_ifaces.values()]
		bmc_vlan = self.get_bmc_vlan()
		host_ifaces = {iface['mac']: iface for iface in self.owner.call('list.host.interface', hosts)}

		for mac, iface in mac_ifaces.items():
			interface = host_ifaces[mac]

			vlan = interface['vlan'] if interface['vlan'] else '1'
			port = iface['port']

			if interface['network'] not in self.networks:
				self.add_vlan(interface['network'], vlan)

			if interface != self.frontend:
				self.owner.addOutput('localhost', f'add interface swp{port} bridge vids {vlan},{bmc_vlan}')
			self.owner.addOutput('localhost', f'add interface swp{port} bridge pvid {vlan}')
			self.owner.addOutput('localhost', f'add interface swp{port} stp bpduguard')
			self.owner.addOutput('localhost', f'add interface swp{port} stp portadminedge')

	def add_vlan(self, network, vlan):
		self.networks[network] = self.owner.call('list.network', [network])[0]
		network = self.networks[network]
		interface = ipaddress.IPv4Interface(f"{network['gateway']}/{network['mask']}")

		self.owner.addOutput('localhost', f'add vlan {vlan} ip address {interface.with_prefixlen}')

		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan}in accept source-ip {interface.network} dest-ip {interface.network}')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan}out accept source-ip {self.frontend["ip"]}/32 dest-ip {interface.network}')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan}in accept source-ip {interface.network} dest-ip {self.frontend["ip"]}/32')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan}in drop source-ip any dest-ip any')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan}out drop source-ip any dest-ip any')
		self.owner.addOutput('localhost', f'add vlan {vlan} acl ipv4 acl{vlan}in inbound')
		self.owner.addOutput('localhost', f'add vlan {vlan} acl ipv4 acl{vlan}out inbound')

	def get_bmc_vlan(self):
		result = subprocess.run('ipmitool lan print'.split(), encoding='utf-8', stdout=subprocess.PIPE)
		try:
			bmc_vlan = re.search(r'802\.1q VLAN ID\s+:\s+(\d+|Disabled)', result.stdout).group(1)
		except (AttributeError, IndexError):
			# No matching line OR no matching group
			bmc_vlan = '4000'  # other default?

		return bmc_vlan if bmc_vlan != 'Disabled' else '4000'

	def get_swp_range(self):
		interfaces = self.switch.run('show interface all json', json_loads=True)
		ports = [int(re.search('\d+', interface).group()) for interface in interfaces if interface.startswith('swp')]
		return f'{min(ports)}-{max(ports)}'

