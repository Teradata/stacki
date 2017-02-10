#! /opt/stack/bin/python
from __future__ import print_function
import os
import subprocess
import traceback
import stack.sql
import stack.password
import stack.ip
import stack.media
import stack.file
import sys
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring

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

	def get(self, attr):
		return getattr(self.data, attr)

	def getDVDPallets(self):
		# packages = [('test', 'ver', 'rel', 'diskId'),
		#		('test2', 'ver2', 'rel', 'diskId')]

		#check if CD is mounted and get list
		packages = []
		media = stack.media.Media()

		media.mountCD()
		rollfile = stack.file.RollFile('/dev/null')
		name, version, release, arch, diskid, foreign = \
			rollfile.getRollInfo()
		diskid = media.getId()

		timestamp, name, arch, disknum, version = media.getCDInfo()
		diskid = media.getId()
		
		if name in [ 'RHEL', 'CentOS' ]:
			release = stack.release
			packages.append((name, version, release, diskid))
		else:
			rolls = media.getRollsFromCD()
			for name, version, release, arch in rolls:
				packages.append((name, version, release, diskid))

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
		f = open(interfaceFile,'w')
		for line in lines:
			f.write('%s\n' % line.strip())
		f.close()

		# Remove the dhcp file if it exists
		ifDhcpFile = '/etc/dhcp/dhclient-%s.conf' % interface
		if os.path.exists(ifDhcpFile):
			os.remove(ifDhcpFile)
		# Force network reconfiguration
		cmd = ['/sbin/ifconfig', interface, addr, 'netmask',netmask]
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
			a = line.split(":", 2)
			d = a[1].strip()
			m = a[2]
			if not (d.find("virbr") > -1 or m.find("loopback") > -1 or \
				m.find("noqueue") > -1):
				n1 = int(m.find("link/ether")) + 11
				n2 = int(m.find("brd")) - 1
				m = m[n1 : n2]
				devices[d] = m

		self.data.devices = devices
		return devices

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
			D = self.data.Kickstart_PrivateDNSServers.split(",")
			try:
				for d in D:
					ip = stack.ip.IPGenerator(d, "255.255.255.255")
			except:
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
				if i != len(n)-1:
					dns += "."
			self.data.Kickstart_PrivateDNSDomain = dns

			#calculate public network interfaces
			try:
				ip = stack.ip.IPGenerator( \
					self.data.Kickstart_PrivateAddress, \
					self.data.Kickstart_PrivateNetmask)
				self.data.Kickstart_PrivateNetwork = ip.get_network()
				self.data.Kickstart_PrivateBroadcast = ip.broadcast()
				self.data.Kickstart_PrivateNetmaskCIDR = ip.cidr()
				self.data.Kickstart_PrivateEthernet = \
					self.data.devices[ \
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
		count = len(dvdlist) + len(netlist)
		if count == 0:
			return (False, "Please select a pallet", "Error")
		else:
			self.data.dvdrolls = []
			self.data.netrolls = []

			if len(dvdlist) > 0:
				self.data.dvdrolls = dvdlist
			if len(netlist) > 0:
				self.data.netrolls = netlist
			return (True, "", "")

	def generateSummary(self):
		#string of pallets
		text = ""
		pallets = []

		if self.data.dvdrolls:
			pallets.extend(self.data.dvdrolls)
		if self.data.netrolls:
			pallets.extend(self.data.netrolls)

		for p in pallets:
			text += '\n' + p['name'] + ' ' + p['version'] + ' ' + p['release'] + ' ' + p['id']

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
		members = [attr for attr in dir(self.data) if not callable(attr) \
			and not attr.startswith("__") and not attr == 'devices' and not \
			attr == 'dvdrolls' and not attr == 'netrolls' and not \
			attr == 'partition']
		for w in members:
			v = getattr(self.data, w)
			f.write(str(w) + ":" + str(v) + os.linesep)
		f.close()

		#create xml elements and write rolls.xml
		#write rolls from dvd
		rolls = Element('rolls')
		if self.data.dvdrolls:
			for w in self.data.dvdrolls:
				roll = SubElement(rolls, 'roll', \
					name=w['name'], \
					version=w['version'], \
					release=w['release'], \
					arch='x86_64', \
					url='http://127.0.0.1/mnt/cdrom/', \
					diskid=w['id'])

		#write rolls from network
		if self.data.netrolls:
			for w in self.data.netrolls:
				roll = SubElement(rolls, 'roll', \
					name=w['name'], \
					version=w['version'], \
					release=w['release'], \
					arch='x86_64', \
					url=w['url'], \
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
