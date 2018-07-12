# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import ipaddress
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch = args[0]

		switch_name = switch['switch']
		switch_interface, *xargs = self.owner.call('list.host.interface', [switch_name])
		self.switch_network, *xargs = self.owner.call('list.network', [switch_interface['network']])
		self.networks = {self.switch_network['network']: self.switch_network}

		# copied; better way?
		# Get frontend ip
		try:
			(self.frontend, *args) = [interface for interface in self.owner.call('list.host.interface', ['localhost'])
				if interface['network'] == switch_interface['network']]
		except:
			raise CommandError(self, f'{self.switch_name} and the frontend do not share a network')

		self.owner.addOutput('localhost', f'<stack:file stack:name="/asdf/{switch_name}/new_config">')

		self.reset()
		self.sync_config()

		self.owner.addOutput('localhost', '</stack:file>')

	def reset(self):
		interface = ipaddress.IPv4Interface(f"{self.switch_network['gateway']}/{self.switch_network['mask']}")

		commands = [
			'del all',
			'add routing defaults datacenter',
			'add routing service integrated-vtysh-config',
			'add routing log syslog informational',
			'add snmp-server listening-address localhost',
			'add bridge bridge pvid 1',
			'add bridge bridge vids 1',
			'add bridge bridge vlan-aware',
			'add bridge pre-up sysctl -w net.ipv4.conf.all.proxy_arp=1',
			'add bridge pre-up sysctl -w net.ipv4.conf.default.proxy_arp=1',
			'add interface eth0',
			'add interface swp21 bridge pvid 1',
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
			f'add vlan 1 ip address {interface.with_prefixlen}',
			'add vlan 1 vlan-id 1',
			'add vlan 1 vlan-raw-device bridge',
			]

		for command in commands:
			self.owner.addOutput('localhost', command)

	def sync_config(self):
		mac_ifaces = {mac_iface['mac']: mac_iface for mac_iface in self.owner.call('list.switch.mac')}#, ['pinghosts=full'])}
		hosts, macs = zip(*[(iface['host'], iface['mac']) for iface in mac_ifaces.values()])
		host_ifaces = [host_iface for host_iface in self.owner.call('list.host.interface', list(hosts)) if host_iface['mac'] in macs]
		for host_iface in host_ifaces:
			iface = mac_ifaces[host_iface['mac']]
			vlan = host_iface['vlan'] if host_iface['vlan'] else '1'

			if host_iface['network'] not in self.networks:
				self.add_vlan(host_iface['network'], vlan)

			self.owner.addOutput('localhost', f"add bridge bridge ports swp{iface['port']}")
			if host_iface != self.frontend:
				self.owner.addOutput('localhost', f"add interface swp{iface['port']} bridge vids {vlan},4000")  # unsure what bmc vid will be (4000)
				self.owner.addOutput('localhost', f"add interface swp{iface['port']} bridge pvid {vlan}")

	def add_vlan(self, network, vlan):
		self.networks[network] = self.owner.call('list.network', [network])[0]
		network = self.networks[network]

		interface = ipaddress.IPv4Interface(f"{network['gateway']}/{network['mask']}")

		self.owner.addOutput('localhost', f'add vlan {vlan} vlan-id {vlan}')
		self.owner.addOutput('localhost', f'add vlan {vlan} vlan-raw-device bridge')
		self.owner.addOutput('localhost', f'add routing route {interface.network} vlan{vlan}')

		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} accept source-ip {interface.network} dest-ip {interface.network}')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} accept source-ip {self.frontend["ip"]}/32 dest-ip {interface.network}')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} accept source-ip {interface.network} dest-ip {self.frontend["ip"]}/32')
		self.owner.addOutput('localhost', f'add acl ipv4 acl{vlan} drop source-ip any dest-ip any')
		self.owner.addOutput('localhost', f'add vlan {vlan} acl ipv4 acl{vlan} inbound')

