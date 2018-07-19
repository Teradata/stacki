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

		switch_name = switch['switch']
		switch_interface = self.owner.call('list.host.interface', [switch_name])[0]
		self.switch_address = switch_interface['ip']
		switch_username = self.owner.getHostAttr(switch_name, 'switch_username')
		switch_password = self.owner.getHostAttr(switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, switch_name, switch_username, switch_password)

		self.switch_network = self.owner.call('list.network', [switch_interface['network']])[0]
		self.networks = {self.switch_network['network']: self.switch_network}
		self.mac_ifaces = {iface['mac']: iface for iface in self.owner.call('list.switch.host')}

		# Get frontend ip
		try:
			self.frontend, *_ = [iface for iface in self.owner.call('list.host.interface', ['localhost'])
				if iface['network'] == switch_interface['network']]
		except:
			raise CommandError(self, f'{self.switch_name} and the frontend do not share a network')

		self.owner.addOutput('localhost', f'<stack:file stack:name="/tmp/{switch_name}/new_config">')
		self.reset()
		self.sync_config()
		self.owner.addOutput('localhost', '</stack:file>')

	def reset(self):
		switch_interface = ipaddress.IPv4Interface(f"{self.switch_network['gateway']}/{self.switch_network['mask']}")
		swps = self.get_swp_range()

		commands = [
			'del all',
			'add routing defaults datacenter',
			'add routing service integrated-vtysh-config',
			'add routing log syslog informational',
			'add snmp-server listening-address localhost',
			f'add bridge bridge ports swp{swps}',
			'add bridge bridge pvid 1',
			'add bridge bridge vids 1',
			'add bridge bridge vlan-aware',
			'add bridge pre-up sysctl -w net.ipv4.conf.all.proxy_arp=1',
			'add bridge pre-up sysctl -w net.ipv4.conf.default.proxy_arp=1',
			'add interface eth0',# ip address dhcp',
			'add loopback lo ip address 127.0.0.1/32',
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
			'add vlan 1 vlan-id 1',
			'add vlan 1 vlan-raw-device bridge',
			]

		for command in commands:
			self.owner.addOutput('localhost', command)

	def sync_config(self):
		hosts, macs = zip(*[(iface['host'], iface['mac']) for iface in self.mac_ifaces.values()])
		bmc_vlan = self.get_bmc_vlan()

		host_ifaces = self.owner.call('list.host.interface', list(hosts))
		host_ifaces = [iface for iface in host_ifaces if iface['mac'] in macs and iface != self.frontend]
		for iface in host_ifaces:
			interface = self.mac_ifaces[iface['mac']]
			vlan = iface['vlan'] if iface['vlan'] else '1'

			if iface['network'] not in self.networks:
				self.add_vlan(iface['network'], vlan)

			self.owner.addOutput('localhost', f"add interface swp{interface['port']} bridge vids {vlan},{bmc_vlan}")
			self.owner.addOutput('localhost', f"add interface swp{interface['port']} bridge pvid {vlan}")

	def add_vlan(self, network, vlan):
		self.networks[network] = self.owner.call('list.network', [network])[0]
		network = self.networks[network]
		interface = ipaddress.IPv4Interface(f"{network['address']}/{network['mask']}")

		self.owner.addOutput('localhost', f'add vlan {vlan} vlan-id {vlan}')
		self.owner.addOutput('localhost', f'add vlan {vlan} vlan-raw-device bridge')
		self.owner.addOutput('localhost', f'add routing route {interface.network} vlan{vlan}')

		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} accept source-ip {interface.network} dest-ip {interface.network}')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} accept source-ip {self.frontend["ip"]}/32 dest-ip {interface.network}')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} accept source-ip {interface.network} dest-ip {self.frontend["ip"]}/32')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} drop source-ip any dest-ip any')
		self.owner.addOutput('localhost', f'add vlan {vlan} acl ipv4 acl{vlan} inbound')

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
		ports = [int(interface[3:]) for interface in interfaces if 'swp' in interface]
		return f'{min(ports)}-{max(ports)}'

