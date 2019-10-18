#! /opt/stack/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import subprocess
import traceback
import stack.password
import stack.probepal
import stack.file
import ipaddress
import socket
from xml.etree.ElementTree import Element, SubElement, ElementTree


class Attr:
	Info_CertificateCountry = "US"
	Info_CertificateLocality = "Solana Beach"
	Info_CertificateOrganization = "StackIQ"
	Info_CertificateState = "California"
	Info_ClusterLatlong = "N32.87 W117.22"
	Info_FQDN = ""
	Kickstart_Keyboard = "us"
	Kickstart_Lang = "en_US"
	Kickstart_Langsupport = "en_US"

	Kickstart_Timezone = ""

	Kickstart_PublicNTPHost = "pool.ntp.org"

	Kickstart_PrivateAddress = ""
	Kickstart_PrivateBroadcast = ""
	Kickstart_PrivateDNSDomain = "local"
	Kickstart_PrivateDNSServers = ""
	Kickstart_PrivateEthernet = ""
	Kickstart_PrivateGateway = ""
	Kickstart_PrivateHostname = ""
	Kickstart_PrivateInterface = ""
	Kickstart_PrivateKickstartHost = ""
	Kickstart_PrivateNTPHost = ""
	Kickstart_PrivateNetmask = ""
	Kickstart_PrivateNetmaskCIDR = ""
	Kickstart_PrivateNetwork = ""
	Kickstart_PrivateNTPHost = ""

	Kickstart_PrivateRootPassword = ""

	nukedisks = False
	devices = {}
	partition = "Automated"
	dvdrolls = None
	netrolls = None


class Data:

	def __init__(self):
		self.data = Attr()

		self.arch = os.uname()[4]
		if self.arch in [ 'i386', 'i486', 'i586', 'i686' ]:
			self.arch = 'i386'
		elif self.arch in [ 'armv7l' ]:
			self.arch = 'armv7hl'

	def get(self, attr):
		return getattr(self.data, attr)

	def mounted(self):
		"Returns true if the /mnt/cdrom device is mounted"

		with open('/proc/mounts') as f:
			for line in f:
				if '/mnt/cdrom' in line:
					return True
		return False


	def mountCD(self, prefix="/"):
		"""Try to mount the CD. Returns 256 if mount failed
		(no disk in drive), 0 on success."""

		if self.mounted():
			return True

		mountpoint = os.path.join(prefix, 'mnt', 'cdrom')

		# loader creates '/tmp/stack-cdrom' -- the cdrom device
		rc = os.system('mount -o ro /tmp/stack-cdrom %s > /dev/null 2>&1' % (mountpoint))

		return rc

	def getDVDPallets(self):
		# packages = [('test', 'ver', 'rel', 'diskId'),
		#		('test2', 'ver2', 'rel', 'diskId')]

		# TODO, mountCD was copied from the deprecated media.py
		# it currently forces the mountpoint to /mnt/cdrom
		self.mountCD()

		pal = stack.probepal.Prober()
		pallets = pal.find_pallets('/mnt/cdrom')

		packages = []
		for pal in pallets['/mnt/cdrom']:
			packages.append((pal.name, pal.version, pal.release, ''))

		return packages

	def validateTimezone(self, zone):
		if not zone:
			return (False, "Please fill out all entries", "Incomplete")
		else:
			self.data.Kickstart_Timezone = zone
			return (True, "", "")

	def setNetwork(self, interface, mac, addr, netmask):
		# Write ifconfig file
		lines = [
			'DEVICE=%s' % interface,
			'HWADDR=%s' % mac,
			'ONBOOT=yes',
			'BOOTPROTO=static',
			'IPADDR=%s' % addr,
			'NETMASK=%s' % netmask
		]
		interfaceFile = '/etc/sysconfig/network-scripts/ifcfg-%s' % interface
		f = open(interfaceFile, 'w')
		for line in lines:
			f.write('%s\n' % line.strip())
		f.close()

		# Remove the dhcp file if it exists
		ifDhcpFile = '/etc/dhcp/dhclient-%s.conf' % interface
		if os.path.exists(ifDhcpFile):
			os.remove(ifDhcpFile)
		# Force network reconfiguration
		cmd = ['/sbin/ifconfig', interface, addr, 'netmask', netmask]
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		# Bring up network
		cmd = ['/sbin/ifconfig', interface, 'up']
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

	def setHostname(self, hostname):
		hostfile = '/etc/sysconfig/network'
		f = open(hostfile, 'w')
		f.write('NETWORKING=yes\n')
		f.write('HOSTNAME=%s\n' % hostname)
		f.close()
		os.system('/bin/hostname %s' % hostname)

	def setResolv(self, domain, servers):
		resolv = '/etc/resolv.conf'
		f = open(resolv, 'w')
		f.write('search %s\n' % domain)
		ns = servers.split(',')
		for nameserver in ns:
			f.write('nameserver %s\n' % nameserver)
		f.close()

	def configNetwork(self):
		#configure network immediately
		self.setNetwork(self.data.Kickstart_PrivateInterface,
			self.data.Kickstart_PrivateEthernet,
			self.data.Kickstart_PrivateAddress,
			self.data.Kickstart_PrivateNetmask)

		# Add default Gateway
		cmd = ['/sbin/route', 'add', 'default', 'gw',
			self.data.Kickstart_PrivateGateway]
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

		# Set hostname of host to Private Hostname
		self.setHostname(self.data.Info_FQDN)

		# Set resolv.conf
		self.setResolv(self.data.Kickstart_PrivateDNSDomain,
			self.data.Kickstart_PrivateDNSServers)

	def getDevices(self):
		#get mac address for interfaces
		devices = {}
		cmd = ['ip', '-o', 'link', 'show']
		output = ''
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		for line in p.stdout.readlines():
			a = line.decode().split(":", 2)
			d = a[1].strip()
			m = a[2]
			if not (d.find("virbr") > -1 or m.find("loopback") > -1 or m.find("noqueue") > -1):
				n1 = int(m.find("link/ether")) + 11
				n2 = int(m.find("brd")) - 1
				m = m[n1 : n2]
				devices[d] = m

		self.data.devices = devices
		return devices

	def validateDomain(self, fqdn):
		hostname = fqdn.split(".")[0]
		if hostname.lower() in ["frontend","backend"]:
			return False, "Cannot have an appliance name as a hostname", "Hostname Error"
		else:
			return True, "", ""

	def validateNetwork(self, tup, config_net=False):

		fqhn, eth, ip, subnet, gateway, dns = tup

		self.data.Info_FQDN = str(fqhn)
		self.data.Kickstart_PrivateInterface = str(eth)
		self.data.Kickstart_PrivateAddress = str(ip)
		self.data.Kickstart_PrivateNetmask = str(subnet)
		self.data.Kickstart_PrivateGateway = str(gateway)
		self.data.Kickstart_PrivateDNSServers = str(dns)

		#incomplete entry
		if not self.data.Kickstart_PrivateInterface or not \
			self.data.Kickstart_PrivateAddress or not \
			self.data.Kickstart_PrivateNetmask or not \
			self.data.Kickstart_PrivateGateway or not \
			self.data.Kickstart_PrivateDNSServers or not \
			self.data.Info_FQDN:
			return (False, "Please fill out all entries", "Incomplete")
		else:
			#invalid dns format
			dns_ips = self.data.Kickstart_PrivateDNSServers.split(",")
			try:
				for ip in dns_ips:
					ip = socket.inet_aton(ip)
			except socket.error:
				print(traceback.format_exc())
				return (False, "DNS entry not in proper format", "Input Error")

			#calculate other attributes
			self.data.Kickstart_PrivateKickstartHost = \
				self.data.Kickstart_PrivateAddress
			self.data.Kickstart_PrivateNTPHost = \
				self.data.Kickstart_PrivateAddress
			#self.data.Kickstart_PrivateHostname =
			#	self.data.Kickstart_PrivateHostname.split(".")[0]

			#calculate public dns domain
			n = self.data.Info_FQDN
			n = n.split(".")
			self.data.Kickstart_PrivateHostname = n.pop(0)
			dns = ""
			for i in range(len(n)):
				dns += n[i]
				if i != len(n) - 1:
					dns += "."
			self.data.Kickstart_PrivateDNSDomain = dns

			#calculate public network interfaces
			try:
				ipnetwork = ipaddress.IPv4Network(
					self.data.Kickstart_PrivateAddress + '/' +
					self.data.Kickstart_PrivateNetmask,
					strict=False)
				self.data.Kickstart_PrivateGateway = str(ipaddress.ip_address(str(self.data.Kickstart_PrivateGateway)))
				self.data.Kickstart_PrivateNetwork = str(ipnetwork.network_address)
				self.data.Kickstart_PrivateBroadcast = str(ipnetwork.broadcast_address)
				self.data.Kickstart_PrivateNetmaskCIDR = str(ipnetwork.prefixlen)
				self.data.Kickstart_PrivateEthernet = self.data.devices[
					self.data.Kickstart_PrivateInterface]
				self.data.devices.pop(self.data.Kickstart_PrivateInterface)

				if config_net:
					self.configNetwork()

				return (True, "", "")
			except:
				print(traceback.format_exc())
				return (False, "Incorrect input", "Input Error")

	def validatePassword(self, pw1, pw2):

		if not pw1 or not pw2:
			return (False, "Please fill out all entries", "Incomplete")

		elif pw1 != pw2:
			return (False, "Passwords do not match", "Incomplete")

		else:
			p = stack.password.Password()

			# encrypt the root password
			self.data.Kickstart_PrivateRootPassword = p.get_crypt_pw(pw1)

			return (True, "", "")

	def validatePartition(self, value):

		if value == 'Automated':
			self.data.partition = 'Automated'
		elif value == 'Manual':
			self.data.partition = 'Manual'
		else:
			return (False, "Not a valid selection", "Error")

		return (True, "", "")

	def validatePallets(self, dvdlist, netlist):
		if len(dvdlist + netlist) == 0:
			return (False, "Please select a pallet", "Error")
		else:
			self.data.dvdrolls = dvdlist
			self.data.netrolls = netlist

			return (True, "", "")

	def generateSummary(self):
		#string of pallets
		text = ""
		pallets = self.data.dvdrolls + self.data.netrolls

		for p in pallets:
			text += '\n' + p['name'] + ' ' + p['version'] + ' ' + p['release']

		#display summary data
		summaryStr = 'Hostname: ' + self.data.Info_FQDN + '\n' + \
			'Timezone: ' + self.data.Kickstart_Timezone + '\n' + \
			'Private Device: ' + \
				self.data.Kickstart_PrivateInterface + '\n' + \
			'Private IP: ' + \
				self.data.Kickstart_PrivateAddress + '\n' + \
			'Private Netmask: ' + \
				self.data.Kickstart_PrivateNetmask + '\n' + \
			'Private Gateway: ' + \
				self.data.Kickstart_PrivateGateway + '\n' + \
			'Private DNS Servers: ' + \
				self.data.Kickstart_PrivateDNSServers + '\n' + \
			'Partition: ' + self.data.partition + '\n\n' + \
			'Pallets:' + str(text)

		return summaryStr

	def writefiles(self):

		#write site.attrs
		f = open('/tmp/site.attrs', 'w')
		members = [attr for attr in dir(self.data) 
			   if not callable(attr) and 
			   not attr.startswith("__") and 
			   not attr == 'devices' and 
			   not attr == 'dvdrolls' and 
			   not attr == 'netrolls' and
			   not attr == 'partition']
		for w in members:
			v = getattr(self.data, w)
			f.write(str(w) + ":" + str(v) + os.linesep)

		#
		# need to add an 'os.version' attribute so configure-partitions.py will work
		#
		f.write('os.version:7.x\n')

		# if hostname isn't explicitly set, list node xml will call 
		# `self.db.getHostname()` which returns localhost
		f.write('hostname:{}\n'.format(self.data.Kickstart_PrivateHostname))

		f.close()

		#create xml elements and write rolls.xml
		#write rolls from dvd
		rolls = Element('rolls')
		for w in self.data.dvdrolls:
			roll = SubElement(rolls, 'roll',
				name=w['name'],
				version=w['version'],
				release=w['release'],
				arch=self.arch,
				url='http://127.0.0.1/mnt/cdrom/',
				diskid=w['id'])

		#write rolls from network
		for w in self.data.netrolls:
			roll = SubElement(rolls, 'roll',
				name=w['name'],
				version=w['version'],
				release=w['release'],
				arch=self.arch,
				url=w['url'],
				diskid='')

		#write to file
		tree = ElementTree(rolls)
		tree.write('/tmp/rolls.xml')

		#write user_partition_info if manual
		if self.data.partition == 'Manual':
			f = open('/tmp/user_partition_info', 'w+')
			f.write('stack manual')
			f.close()

		return (True, '', '')
