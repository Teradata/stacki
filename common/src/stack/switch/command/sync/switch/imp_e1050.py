# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import ipaddress
import pexpect
import re
import stack.commands
from stack.exception import CommandError
from stack.switch.e1050 import SwitchCelesticaE1050


class Implementation(stack.commands.Implementation):

	# all netID/mask assumptions are possibly invalid

	def run(self, args):
		self.switch_name = args[0]
		self.svis = self.owner.call('list.host.interface', [self.switch_name, 'expanded=True'])
		access_interface = [svi for svi in self.svis if not svi['vlan']][0]  # temporary
		# infer that no vlan value means vlan 1?
		self.svis.remove(access_interface)  # how to modify access iface? Exclude for now

		# copied; better way?
		# Get frontend ip
		try:
			(self.frontend, *args) = [host for host in self.owner.call('list.host.interface', ['localhost'])
				if host['network'] == access_interface['network']]
		except:
			raise CommandError(self, f'{self.switch_name} and the frontend do not share a network')

		# handle bad ip/creds?
		self.switch_address = access_interface['ip']
		self.switch_username = self.owner.getHostAttr(self.switch_name, 'switch_username')
		self.switch_password = self.owner.getHostAttr(self.switch_name, 'switch_password')
		self.switch = SwitchCelesticaE1050(self.switch_address, self.switch_name, self.switch_username, self.switch_password)

		# self.ssh_copy_id()
		# self.reset()
		# self.vlans()
		# self.vlan_members()
		print('merp')

		# print(self.switch.rpc_req_text(cmd='pending'))
		# self.switch.rpc_req_text(cmd='abort')
		# self.switch.rpc_req_text(cmd='commit')

		# set switch host name?

	# does this belong in switch class?
	def ssh_copy_id(self):
		child = pexpect.spawn(f'ssh-copy-id -i /root/.ssh/id_rsa.pub {self.switch_username}@{self.switch_address}')
		try:
			child.expect('password')
			child.sendline(self.switch_password)
			child.expect(pexpect.EOF)

			self.owner.addOutput(f'{self.switch_name}:', re.search(r'Number of (.+)', child.before.decode('utf-8')).group())
		except pexpect.EOF:
			self.owner.addOutput(f'{self.switch_name}:', re.findall(r'WARNING: (.+)', child.before.decode('utf-8'))[0])

	def reset(self):
		commands = ['del all',
				'add routing defaults datacenter',
				'add routing service integrated-vtysh-config',
				'add routing log syslog informational',
				'add snmp-server listening-address localhost',
				'add bridge bridge pvid 1',
				'add bridge bridge vids 1',
				'add bridge bridge vlan-aware',
				'add bridge pre-up sysctl -w net.ipv4.conf.all.proxy_arp=1',
				'add bridge pre-up sysctl -w net.ipv4.conf.default.proxy_arp=1',
				'add interface eth0',  # keep eth0?
				'add interface swp21 bridge pvid 1',
				'add loopback lo ip address 127.0.0.1/32',
				'add time zone Etc/UTC',
				'add time ntp server 0.cumulusnetworks.pool.ntp.org iburst',
				'add time ntp server 1.cumulusnetworks.pool.ntp.org iburst',
				'add time ntp server 2.cumulusnetworks.pool.ntp.org iburst',
				'add time ntp server 3.cumulusnetworks.pool.ntp.org iburst',
				'add time ntp source eth0',  # keep eth0?
				'add dot1x radius accounting-port 1813',
				'add dot1x eap-reauth-period 0',
				'add dot1x radius authentication-port 1812',
				'add dot1x mab-activation-delay 30',
				'add bridge bridge ports swp21',  # not guaranteed; how to set?
				'add vlan 1 ip address 10.2.232.32/24',  # could change if access iface changes; how to handle?
				'add vlan 1 vlan-id 1',
				'add vlan 1 vlan-raw-device bridge',
				]

		for command in commands:
			self.switch.rpc_req_text(cmd=command)

	def vlans(self):
		for interface in self.svis:
			vlan = interface['vlan']
			interface = ipaddress.IPv4Interface(f"{interface['gateway']}/{interface['mask']}")  # different name?

			self.switch.rpc_req_text(cmd=f"add vlan {vlan} ip address {interface.ip}")
			self.switch.rpc_req_text(cmd=f'add vlan {vlan} vlan-id {vlan}')
			self.switch.rpc_req_text(cmd=f'add vlan {vlan} vlan-raw-device bridge')

			self.switch.rpc_req_text(cmd=f'add acl ipv4 acl{vlan} accept source-ip {interface.network} dest-ip {interface.network}')
			self.switch.rpc_req_text(cmd=f'add acl ipv4 acl{vlan} accept source-ip {self.frontend["ip"]}/32 dest-ip {interface.network}')
			self.switch.rpc_req_text(cmd=f'add acl ipv4 acl{vlan} accept source-ip {interface.network} dest-ip {self.frontend["ip"]}/32')
			self.switch.rpc_req_text(cmd=f'add acl ipv4 acl{vlan} drop source-ip any dest-ip any')
			self.switch.rpc_req_text(cmd=f'add vlan {vlan} acl ipv4 acl{vlan} inbound')

	def vlan_members(self):
		# better names
		mac_ifaces = {}
		for item in self.owner.call('list.switch.mac'):  # pinghost=True (broken)
			mac_ifaces[item['mac']] = {'iface': 'swp' + item['port'], 'vlan': item['vlan']}  # add vlan at this point or not?
			# if so, why not just rpc_req_text here? all the info is here
			# but might 'list switch mac' include non-vlan ports in the future?

		host_ifaces = self.owner.call('list.host.interface', ["where appliance != 'switch'"])
		for host_iface in host_ifaces:
			iface = mac_ifaces[host_iface['mac']]

			self.switch.rpc_req_text(cmd=f'add bridge bridge ports {iface["iface"]}')
			self.switch.rpc_req_text(cmd=f"add interface {iface['iface']} bridge vids {host_iface['vlan']}, 4000")  # unsure what bmc vid will be (4000)
			self.switch.rpc_req_text(cmd=f"add interface {iface['iface']} bridge pvid {host_iface['vlan']}")

