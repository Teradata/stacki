# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import ipaddress

import stack.commands
from stack.commands import Warn, HostArgProcessor
import stack.text

header = """
ddns-update-style none;

option space PXE;
option PXE.mtftp-ip    code 1 = ip-address;
option PXE.mtftp-cport code 2 = unsigned integer 16;
option PXE.mtftp-sport code 3 = unsigned integer 16;
option PXE.mtftp-tmout code 4 = unsigned integer 8;
option PXE.mtftp-delay code 5 = unsigned integer 8;

option client-arch code 93 = unsigned integer 16;
"""

filename = """	if option client-arch = 00:07 {
		filename "uefi/shim.efi";
	} else {
		filename "pxelinux.0";
	}"""


class Command(HostArgProcessor, stack.commands.report.command):
	"""
	Output the DHCP server configuration file.

	<example cmd='report dhcpd'>
	Output the DHCP server configuration file.
	</example>
	"""

	def writeDhcpDotConf(self):
		self.addOutput('', '<stack:file stack:name="/etc/dhcp/dhcpd.conf">')

		self.addOutput('', stack.text.DoNotEdit())
		self.addOutput('', '%s' % header)

		# Build a dictionary of DHCPD server addresses
		# for each subnet that serves PXE (DHCP).

		servers = {}
		for row in self.db.select("""
			s.name, n.ip from nodes nd, subnets s, networks n
			where s.pxe=TRUE and nd.name=%s
			and n.node=nd.id and s.id=n.subnet
		""", (self.db.getHostname(),)):
			servers[row[0]]	   = row[1]
			servers['default'] = row[1]

		if len(servers) > 2:
			del servers['default']

		shared_networks = {}
		for (netname, network, netmask, gateway, zone, device) in self.db.select("""
			s.name, s.address, s.mask, s.gateway, s.zone, n.device
			from subnets s, networks n
			where pxe=TRUE and node=(select id from nodes where name=%s)
			and subnet=s.id
		""", (self.db.getHostname(),)):

			if self.os == 'sles':
				device = device.split('.')[0].split(':')[0]
				dhchp_settings = (netname, network, netmask, gateway, zone)
				if device in shared_networks:
					if dhchp_settings not in shared_networks[device]:
						shared_networks[device].append(dhchp_settings)
				else:
					shared_networks[device] = [dhchp_settings]

			else:
				self.addOutput('', '\nsubnet %s netmask %s {'
					% (network, netmask))

				self.addOutput('', '\tdefault-lease-time\t\t1200;')
				self.addOutput('', '\tmax-lease-time\t\t\t1200;')

				ipnetwork = ipaddress.IPv4Network(network + '/' + netmask)
				self.addOutput('', '\toption routers\t\t\t%s;' % gateway)
				self.addOutput('', '\toption subnet-mask\t\t%s;' % netmask)
				self.addOutput('', '\toption broadcast-address\t%s;' %
					ipnetwork.broadcast_address)
				self.addOutput('', '}\n')
		#
		# if sles, add shared_network block to interfaces with multiple subnets
		#
		if self.os == 'sles':
			for device in shared_networks.keys():
				sn = shared_networks[device]
				if len(sn) == 1:
					for (netname, network, netmask, gateway, zone) in sn:
						self.addOutput('', '\nsubnet %s netmask %s {'
							% (network, netmask))

						self.addOutput('', '\tdefault-lease-time\t\t1200;')
						self.addOutput('', '\tmax-lease-time\t\t\t1200;')

						ipnetwork = ipaddress.IPv4Network(network + '/' + netmask)
						self.addOutput('', '\toption routers\t\t\t%s;' % gateway)
						self.addOutput('', '\toption subnet-mask\t\t%s;' % netmask)
						self.addOutput('', '\toption broadcast-address\t%s;' %
							ipnetwork.broadcast_address)
						self.addOutput('', '}\n')
				else:
					self.addOutput('', '\nshared-network %s {' % device)
					for (netname, network, netmask, gateway, zone) in sn:
						self.addOutput('', '\n\tsubnet %s netmask %s {'
							% (network, netmask))

						self.addOutput('', '\t\tdefault-lease-time\t\t1200;')
						self.addOutput('', '\t\tmax-lease-time\t\t\t1200;')

						ipnetwork = ipaddress.IPv4Network(network + '/' + netmask)
						self.addOutput('', '\t\toption routers\t\t\t%s;' % gateway)
						self.addOutput('', '\t\toption subnet-mask\t\t%s;' % netmask)
						self.addOutput('', '\t\toption broadcast-address\t%s;' %
							ipnetwork.broadcast_address)
						self.addOutput('', '\t}\n')
					self.addOutput('', '}\n')

		data = {}
		for host in self.call('list.host'):
			data[host['host']] = []

		host_devices = {}
		interfaces = self.call('list.host.interface')
		for interface in interfaces:
			host = interface['host']
			mac = interface['mac']
			ip = interface['ip']
			device = interface['interface']
			channel = interface['channel']

			other_interfaces = [iface['interface'] for iface in interfaces
					    if iface['host'] == host and iface['interface'] != device]

			if channel:
				if device == 'ipmi' and not ip:
					Warn(f'WARNING: skipping IPMI interface on host "{host}" - interface has a channel but no IP')
					continue
				elif device != 'ipmi' and channel not in other_interfaces:
					Warn(f'WARNING: skipping interface "{device}" on host "{host}" - '
					     f'interface has channel "{channel}" that does not match any other interface on the host')
					continue
			if host in host_devices:
				if device in host_devices[host]:
					Warn(f'WARNING: skipping interface "{device}" on host "{host}" - duplicate interface detected')
					continue
				else:
					host_devices[host].append(device)
			elif host:
				host_devices[host] = [device]

			if host and mac:
				data[host].append((mac, ip, device))

		for name in data.keys():
			kickstartable = self.str2bool(self.getHostAttr(name, 'kickstartable'))
			aws = self.str2bool(self.getHostAttr(name, 'aws'))
			mac = None
			ip  = None
			dev = None

			#
			# look for a physical private interface that has an
			# IP address assigned to it.
			#
			for (mac, ip, dev) in data[name]:
				if not ip:
					try:
						ip = self.resolve_ip(name, dev)
					except IndexError:
						Warn(f'WARNING: skipping interface "{device}" on host "{host}" - duplicate interface detected')
						continue
				netname = None
				if ip:
					r = self.db.select("""
						s.name from subnets s, networks nt, nodes n
						where nt.node=n.id and n.name=%s
						and nt.subnet=s.id and s.pxe=TRUE and nt.ip=%s
					""", (name, ip))

					if r:
						(netname, ) = r[0]
				if ip and mac and dev and netname and not aws:
					self.addOutput('', '\nhost %s.%s.%s {' %
						(name, netname, dev))
					self.addOutput('', '\toption host-name\t"%s";' % name)

					self.addOutput('', '\thardware ethernet\t%s;' % mac)
					self.addOutput('', '\tfixed-address\t\t%s;' % ip)

					if kickstartable:

						self.addOutput('', filename)
						server = servers.get(netname)
						if not server:
							server = servers.get('default')

						self.addOutput('','\tserver-name\t\t"%s";'
							% server)
						self.addOutput('','\tnext-server\t\t%s;'
							% server)

					self.addOutput('', '}')

		self.addOutput('', '</stack:file>')

	def resolve_ip(self, host, device):
		"""
		Attempts to resolve the IP address of a host interface that lacks an address
		(for example, if the interface is part of a bond).
		"""

		(ip, channel) = self.db.select("""
			nt.ip, nt.channel from networks nt, nodes n
			where n.name=%s and nt.device=%s and nt.node=n.id
		""", (host, device))[0]

		if channel:
			return self.resolve_ip(host, channel)
		return ip

	def writeDhcpSysconfig(self):
		self.addOutput('', '<stack:file stack:name="/etc/sysconfig/dhcpd">')
		self.addOutput('', stack.text.DoNotEdit())

		devices = set()
		for device, in self.db.select("""
			device from networks n, subnets s
			where n.node=(select id from nodes where name=%s)
			and s.pxe=TRUE and n.ip is not NULL and n.subnet=s.id
		""", (self.db.getHostname(),)):

			# since sles doesn't use seperate config files for virtual 
			# interfaces, we only add the actual interface to devices
			if self.os == 'sles':
				if ':' not in device:
					devices.add(device)
			else:
				devices.add(device)

		devices = ' '.join(sorted(devices))

		if self.os == 'redhat':
			self.addOutput('', f'DHCPDARGS="{devices}"')
		if self.os == 'sles':
			self.addOutput('', f'DHCPD_INTERFACE="{devices}"')

		self.addOutput('', '</stack:file>')

	def run(self, params, args):
		self.beginOutput()
		self.writeDhcpDotConf()
		self.writeDhcpSysconfig()
		self.endOutput(padChar='')
