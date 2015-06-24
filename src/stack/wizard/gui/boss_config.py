#!/opt/stack/bin/python
import os
import subprocess
import stack.sql
import stack.password
import stack.ip
import stack.media
import stack.file
import wx
import sys
import traceback
import urllib2
import wx.lib.newevent
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import pickle

(PageChangeEvent, EVT_PAGE_CHANGE) = wx.lib.newevent.NewEvent()

def setNetwork(interface, mac, addr, netmask):
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

def setHostname(hostname):
	hostfile = '/etc/sysconfig/network'
	f = open(hostfile, 'w')
	f.write('NETWORKING=yes\n')
	f.write('HOSTNAME=%s\n' % hostname)
	f.close()
	os.system('/bin/hostname %s' % hostname)

def setResolv(domain, servers):
	resolv = '/etc/resolv.conf'
	f = open(resolv, 'w')
	f.write('search %s\n' % domain)
	ns = servers.split(',')
	for nameserver in ns:
		f.write('nameserver %s\n' % nameserver)
	f.close()

class Data:
	HttpConf = "/etc/httpd/conf"
	HttpConfigDirExt = "/etc/httpd/conf.d"
	HttpRoot = "/var/www/html"
	Info_CertificateCountry = "US"
	Info_CertificateLocality = "Solana Beach"
	Info_CertificateOrganization = "StackIQ"
	Info_CertificateState = "California"
	Info_ClusterContact = ""
	Info_ClusterLatlong = "N32.87 W117.22"
	Info_ClusterName = ""
	Info_ClusterURL = ""
	Kickstart_DistroDir = "/export/stack"
	Kickstart_Keyboard = "us"
	Kickstart_Lang = "en_US"
	Kickstart_Langsupport = "en_US"

	Kickstart_Timezone = ""
	RootDir = "/root"

	Kickstart_PublicAddress = ""
	Kickstart_PublicBroadcast = ""
	Kickstart_PublicDNSDomain = ""
	Kickstart_PublicDNSServers = ""
	Kickstart_PublicEthernet = ""
	Kickstart_PublicGateway = ""
	Kickstart_PublicHostname = ""
	Kickstart_PublicInterface = ""
	Kickstart_PublicKickstartHost = ""
	Kickstart_PublicNTPHost = "pool.ntp.org"
	Kickstart_PublicNetmask = ""
	Kickstart_PublicNetmaskCIDR = ""
	Kickstart_PublicNetwork = ""

	Kickstart_PrivateAddress = ""
	Kickstart_PrivateBroadcast = ""
	Kickstart_PrivateDNSDomain = "local"
	Kickstart_PrivateDNSServers = ""
	Kickstart_PrivateEthernet = ""
	Kickstart_PrivateGateway = ""
	Kickstart_PrivateHostname = ""
	Kickstart_PrivateInterface = ""
	Kickstart_PrivateKickstartCGI = "sbin/kickstart.cgi"
	Kickstart_PrivateKickstartHost = ""
	Kickstart_PrivateNTPHost = ""
	Kickstart_PrivateNetmask = ""
	Kickstart_PrivateNetmaskCIDR = ""
	Kickstart_PrivateNetwork = ""
	Kickstart_PrivateSyslogHost = ""
	Kickstart_PrivateKickstartBasedir = "distributions"

	Kickstart_PrivateRootPassword = ""
	Kickstart_PrivateDjangoRootPassword = ""
	Kickstart_PrivateMD5RootPassword = ""
	Kickstart_PrivatePortableRootPassword = ""
	Kickstart_PrivateSHARootPassword = ""

	nukedisks = False
	devices = {}
	partition = "Automated"
	dvdrolls = None
	netrolls = None

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)	


class Page1(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		sizer = wx.GridBagSizer(3, 4)

		#get the logo image
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#get the help image
		png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                helpBitmap1 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap2 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap3 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap4 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		#top label
		label = wx.StaticText(self, label="Cluster Information")
		sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#labels
                name = wx.StaticText(self, label="Cluster Name")
		domain = wx.StaticText(self, label="Fully-Qualified Host Name")
                email = wx.StaticText(self, label="Email")
                time = wx.StaticText(self, label="Timezone")

		#input text
		self.tc1 = wx.TextCtrl(self, value=self.data.Info_ClusterName)
                self.tc2 = wx.TextCtrl(self, value=self.data.Kickstart_PublicHostname)
                self.tc3 = wx.TextCtrl(self, value=self.data.Info_ClusterContact)

		self.tc1.SetForegroundColour(wx.BLACK)
		self.tc1.SetBackgroundColour(wx.WHITE)
		self.tc2.SetForegroundColour(wx.BLACK)
		self.tc2.SetBackgroundColour(wx.WHITE)
		self.tc3.SetForegroundColour(wx.BLACK)
		self.tc3.SetBackgroundColour(wx.WHITE)

		#help bubbles
		helpBitmap1.SetToolTip(wx.ToolTip("Name of your cluster"))
		helpBitmap2.SetToolTip(wx.ToolTip("This must be the fully-qualified domain name\n(e.g., dev.stacki.com)"))
		helpBitmap3.SetToolTip(wx.ToolTip("Email of the system administrator"))
		helpBitmap4.SetToolTip(wx.ToolTip("Select a timezone for this cluster"))

		#time zone combo box
		timezones = tuple(line.strip() for line in open('/opt/stack/bin/timezones.txt'))
                self.cb = wx.ComboBox(self, pos=(50, 30), size=(200, -1), choices=timezones, style=wx.CB_READONLY)
		self.cb.SetForegroundColour(wx.BLACK)
		self.cb.SetBackgroundColour(wx.WHITE)

		#put elements into form
		fgs = wx.FlexGridSizer(4, 3, 9, 25)
		fgs.AddMany([(name), (helpBitmap1), (self.tc1, 1, wx.EXPAND),
                        (domain), (helpBitmap2), (self.tc2, 1, wx.EXPAND),
                        (email), (helpBitmap3), (self.tc3, 1, wx.EXPAND),
                        (time), (helpBitmap4), (self.cb, 1, wx.EXPAND)])
		fgs.AddGrowableCol(2, 2)
		sizer.Add(fgs, pos=(2, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#next button
		goto_page2 = wx.Button(self, label="Continue")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		#hbox.Add(goto_page1, 0, wx.RIGHT, 20)
		hbox.Add(goto_page2, 0, wx.RIGHT, 0)
		sizer.Add(goto_page2, pos=(3, 4), flag=wx.RIGHT|wx.BOTTOM, border=20)

		sizer.AddGrowableCol(1)
		sizer.AddGrowableRow(2)
		self.SetSizerAndFit(sizer)

		#bind event to the next button
		goto_page2.Bind(wx.EVT_BUTTON, self.OnPage2)

	def OnPage2(self, event):
		self.data.Info_ClusterName = str(self.tc1.Value)
		self.data.Kickstart_PublicHostname = str(self.tc2.Value)
		self.data.Info_ClusterContact = str(self.tc3.Value)
		self.data.Kickstart_Timezone = str(self.cb.Value)
		self.data.Info_ClusterURL = "http://" + self.data.Kickstart_PublicHostname + "/"

		if not self.data.Info_ClusterName or not self.data.Kickstart_PublicHostname or not \
			self.data.Info_ClusterContact or not self.data.Kickstart_Timezone:
                	wx.MessageBox('Please fill out all entries', 'Incomplete', wx.OK | wx.ICON_ERROR)	
		else:
			self.data.Kickstart_PrivateHostname = self.data.Kickstart_PublicHostname.split(".")[0]

			#calculate public dns domain
			n = self.data.Kickstart_PublicHostname
			n = n.split(".")
			n.pop(0)
			dns = ""
			for i in range(len(n)):
				dns += n[i]
				if i != len(n)-1:
					dns += "."
			self.data.Kickstart_PublicDNSDomain = dns
			wx.PostEvent(self.parent, PageChangeEvent(page=Page2))

class Page2(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#get mac address for interfaces
		devices = {}
		cmd = ['ip', '-o', 'link', 'show']
		output = ''
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		for line in p.stdout.readlines():
			a = line.split(":", 2)
			d = a[1].strip()
			m = a[2]
			if not (d.find("virbr") > -1 or m.find("loopback") > -1 or m.find("noqueue") > -1):
				n1 = int(m.find("link/ether")) + 11
				n2 = int(m.find("brd")) - 1
				m = m[n1 : n2]
				devices[d] = m
		self.data.devices = devices

		sizer = wx.GridBagSizer(3, 4)

		#get the logo image
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#get the help image
		png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                helpBitmap1 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap2 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap3 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap4 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap5 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		#form
		fgs = wx.FlexGridSizer(5, 3, 9, 25)

                d = wx.StaticText(self, label="Devices")
                ip = wx.StaticText(self, label="IP")
                mask = wx.StaticText(self, label="Netmask")
                gw = wx.StaticText(self, label="Gateway")
                dns = wx.StaticText(self, label="DNS Servers")

                self.tc1 = wx.TextCtrl(self, value=self.data.Kickstart_PublicAddress)
                self.tc2 = wx.TextCtrl(self, value=self.data.Kickstart_PublicNetmask)
                self.tc3 = wx.TextCtrl(self, value=self.data.Kickstart_PublicGateway)
                self.tc4 = wx.TextCtrl(self, value=self.data.Kickstart_PublicDNSServers)

		self.tc1.SetForegroundColour(wx.BLACK)
		self.tc1.SetBackgroundColour(wx.WHITE)
		self.tc2.SetForegroundColour(wx.BLACK)
		self.tc2.SetBackgroundColour(wx.WHITE)
		self.tc3.SetForegroundColour(wx.BLACK)
		self.tc3.SetBackgroundColour(wx.WHITE)
		self.tc4.SetForegroundColour(wx.BLACK)
		self.tc4.SetBackgroundColour(wx.WHITE)

		#help bubbles
		helpBitmap1.SetToolTip(wx.ToolTip("This is the interface that connects the frontend to the outside network"))
		helpBitmap2.SetToolTip(wx.ToolTip("IP address for the device"))
		helpBitmap3.SetToolTip(wx.ToolTip("Netmask for the device"))
		helpBitmap4.SetToolTip(wx.ToolTip("IP address of your public gateway"))
		helpBitmap5.SetToolTip(wx.ToolTip("Supply a comma separated list of your DNS servers if you have more than one"))

		#list of devices
                devices = []
		for w in self.data.devices:
			devices.append(w)
		devices = sorted(devices)
                self.cb = wx.ComboBox(self, pos=(50, 30), choices=devices, style=wx.CB_READONLY)
		self.cb.SetForegroundColour(wx.BLACK)
		self.cb.SetBackgroundColour(wx.WHITE)

                fgs.AddMany([(d), (helpBitmap1), (self.cb, 1, wx.EXPAND),
                        (ip), (helpBitmap2), (self.tc1, 1, wx.EXPAND),
                        (mask), (helpBitmap3), (self.tc2, 1, wx.EXPAND),
                        (gw), (helpBitmap4), (self.tc3, 1, wx.EXPAND),
                        (dns), (helpBitmap5), (self.tc4, 1, wx.EXPAND)])

		fgs.AddGrowableCol(2, 2)
		sizer.Add(fgs, pos=(2, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#top label
		label = wx.StaticText(self, label='Public Network')
		sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#next button
		goto_page1 = wx.Button(self, label="Back")
		goto_page3 = wx.Button(self, label="Continue")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page1, 0, wx.RIGHT, 20)
		hbox.Add(goto_page3)
		sizer.Add(hbox, pos=(3, 4), flag=wx.RIGHT|wx.BOTTOM, border=20)

		sizer.AddGrowableCol(1)
		sizer.AddGrowableRow(2)
		self.SetSizerAndFit(sizer)

		#bind event to the buttons
		goto_page1.Bind(wx.EVT_BUTTON, self.OnPage1)
		goto_page3.Bind(wx.EVT_BUTTON, self.OnPage3)

	def OnPage3(self, event):
		self.data.Kickstart_PublicInterface = str(self.cb.Value)
		self.data.Kickstart_PublicAddress = str(self.tc1.Value)
		self.data.Kickstart_PublicNetmask = str(self.tc2.Value)
		self.data.Kickstart_PublicGateway = str(self.tc3.Value)
		self.data.Kickstart_PublicDNSServers = str(self.tc4.Value)
		self.data.Kickstart_PublicKickstartHost = self.data.Kickstart_PublicAddress

		#incomplete entry
		if not self.data.Kickstart_PublicInterface or not self.data.Kickstart_PublicAddress or not \
			self.data.Kickstart_PublicNetmask or not self.data.Kickstart_PublicGateway or not \
			self.data.Kickstart_PublicDNSServers:
                	wx.MessageBox('Please fill out all entries', 'Incomplete', wx.OK | wx.ICON_ERROR)	
		else:
			#calculate public network interfaces
			try:
				ip = stack.ip.IPGenerator(self.data.Kickstart_PublicAddress, \
					self.data.Kickstart_PublicNetmask)
				self.data.Kickstart_PublicNetwork = ip.get_network()
				self.data.Kickstart_PublicBroadcast = ip.broadcast()
				self.data.Kickstart_PublicNetmaskCIDR = ip.cidr()
				self.data.Kickstart_PublicEthernet = self.data.devices[self.data.Kickstart_PublicInterface]
				self.data.devices.pop(self.data.Kickstart_PublicInterface)

				#configure network immediately
				setNetwork(self.data.Kickstart_PublicInterface,
					self.data.Kickstart_PublicEthernet,
					self.data.Kickstart_PublicAddress,
					self.data.Kickstart_PublicNetmask)

				# Add default Gateway
				cmd = ['/sbin/route', 'add', 'default', 'gw',
					self.data.Kickstart_PublicGateway]
				p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

				# Set hostname of host to Public Hostname
				setHostname(self.data.Kickstart_PublicHostname)

				# Set resolv.conf
				setResolv(self.data.Kickstart_PublicDNSDomain,
					self.data.Kickstart_PublicDNSServers)
			except:
                		wx.MessageBox('Incorrect input', 'Input Error', wx.OK | wx.ICON_ERROR)
				return
			wx.PostEvent(self.parent, PageChangeEvent(page=Page3))

	def OnPage1(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page1))

class Page3(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		sizer = wx.GridBagSizer(3, 4)

		#get the logo image
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#get the help image
		png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                helpBitmap1 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap2 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap3 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		#form
		fgs = wx.FlexGridSizer(4, 3, 9, 25)

                d = wx.StaticText(self, label="Devices")
                ip = wx.StaticText(self, label="IP")
                mask = wx.StaticText(self, label="Netmask")

		#input
                self.tc1 = wx.TextCtrl(self, value=self.data.Kickstart_PrivateAddress)
                self.tc2 = wx.TextCtrl(self, value=self.data.Kickstart_PrivateNetmask)

		self.tc1.SetForegroundColour(wx.BLACK)
		self.tc1.SetBackgroundColour(wx.WHITE)
		self.tc2.SetForegroundColour(wx.BLACK)
		self.tc2.SetBackgroundColour(wx.WHITE)

		#help bubbles
		helpBitmap1.SetToolTip(wx.ToolTip("This is the interface that connects the frontend to the compute nodes"))
		helpBitmap2.SetToolTip(wx.ToolTip("IP address for the device"))
		helpBitmap3.SetToolTip(wx.ToolTip("Netmask for the device"))

		#list of devices
                devices = []
		for w in self.data.devices:
			devices.append(w)
		devices = sorted(devices)
                self.cb = wx.ComboBox(self, pos=(50, 30), choices=devices, style=wx.CB_READONLY)
		self.cb.SetForegroundColour(wx.BLACK)
		self.cb.SetBackgroundColour(wx.WHITE)

                fgs.AddMany([(d), (helpBitmap1), (self.cb, 1, wx.EXPAND),
                        (ip), (helpBitmap2), (self.tc1, 1, wx.EXPAND),
                        (mask), (helpBitmap3), (self.tc2, 1, wx.EXPAND)])

                fgs.AddGrowableCol(2, 2)	
		sizer.Add(fgs, pos=(2, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#top label
		label = wx.StaticText(self, label='Private Network')
		sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#next button
		goto_page4 = wx.Button(self, label="Continue")
		goto_page1 = wx.Button(self, label="Back")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page1, 0, wx.RIGHT, 20)
		hbox.Add(goto_page4)
		sizer.Add(hbox, pos=(3, 4), flag=wx.RIGHT|wx.BOTTOM, border=20)

		#set sizer
		sizer.AddGrowableCol(1)
		sizer.AddGrowableCol(2)
		self.SetSizerAndFit(sizer)

		#bind event to the next button
		goto_page4.Bind(wx.EVT_BUTTON, self.OnPage4)
		goto_page1.Bind(wx.EVT_BUTTON, self.OnPage2)

	def OnPage4(self, event):
		self.data.Kickstart_PrivateInterface = str(self.cb.Value)
		self.data.Kickstart_PrivateAddress = str(self.tc1.Value)
		self.data.Kickstart_PrivateNetmask = str(self.tc2.Value)

		#incomplete entries
		if not self.data.Kickstart_PrivateInterface or not self.data.Kickstart_PrivateAddress or not \
			self.data.Kickstart_PrivateNetmask:
                	wx.MessageBox('Please fill out all entries', 'Incomplete', wx.OK | wx.ICON_ERROR)	
		else:
			self.data.Kickstart_PrivateKickstartHost = self.data.Kickstart_PrivateAddress
			self.data.Kickstart_PrivateNTPHost = self.data.Kickstart_PrivateAddress
			self.data.Kickstart_PrivateGateway = self.data.Kickstart_PrivateAddress
			self.data.Kickstart_PrivateDNSServers = self.data.Kickstart_PrivateAddress
			self.data.Kickstart_PrivateSyslogHost = self.data.Kickstart_PrivateAddress

			#calculate private network interfaces
			try:
				ip = stack.ip.IPGenerator(self.data.Kickstart_PrivateAddress, \
					self.data.Kickstart_PrivateNetmask)
				self.data.Kickstart_PrivateNetwork = ip.get_network()
				self.data.Kickstart_PrivateBroadcast = ip.broadcast()
				self.data.Kickstart_PrivateNetmaskCIDR = ip.cidr()
				self.data.Kickstart_PrivateEthernet = self.data.devices[self.data.Kickstart_PrivateInterface]

				#configure network immediately
				setNetwork(self.data.Kickstart_PrivateInterface,
					self.data.Kickstart_PrivateEthernet,
					self.data.Kickstart_PrivateAddress,
					self.data.Kickstart_PrivateNetmask)
			except:
                		wx.MessageBox('Please check IP and Netmask input', 'Input Error', wx.OK | wx.ICON_ERROR)
				return
			wx.PostEvent(self.parent, PageChangeEvent(page=Page4))

	def OnPage2(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page2))


class Page4(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		self.sizer = wx.GridBagSizer(2, 4)

		#get the logo image
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		self.sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#get the help image
		png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                helpBitmap1 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap2 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		#form
		fgs = wx.FlexGridSizer(3, 3, 9, 25)

		pass1 = wx.StaticText(self, label="Password")
		pass2 = wx.StaticText(self, label="Confirm Password")

		#input
		self.tc1 = wx.TextCtrl(self, style=wx.TE_PASSWORD)
		self.tc2 = wx.TextCtrl(self, style=wx.TE_PASSWORD)

		self.tc1.SetForegroundColour(wx.BLACK)
		self.tc1.SetBackgroundColour(wx.WHITE)
		self.tc2.SetForegroundColour(wx.BLACK)
		self.tc2.SetBackgroundColour(wx.WHITE)

		#help bubbles
		helpBitmap1.SetToolTip(wx.ToolTip("The root password for this cluster"))
		helpBitmap2.SetToolTip(wx.ToolTip("Confirm your password"))

		fgs.AddMany([(pass1), (helpBitmap1), (self.tc1, 1, wx.EXPAND),
			(pass2), (helpBitmap2), (self.tc2, 1, wx.EXPAND)])

		fgs.AddGrowableCol(2, 2)
		self.sizer.Add(fgs, pos=(2, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#top label
		label = wx.StaticText(self, label='Setup Password')
		self.sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#next button
		goto_page5 = wx.Button(self, label="Continue")
		goto_page3 = wx.Button(self, label="Back")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page3, 0, wx.RIGHT, 20)
		hbox.Add(goto_page5, 0, flag=wx.ALIGN_RIGHT)
		self.sizer.Add(hbox, pos=(3, 4), flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, border=20)

		#set sizer
		self.sizer.AddGrowableCol(1)
		self.sizer.AddGrowableCol(2)
		self.SetSizerAndFit(self.sizer)

		#bind event to the next button
		goto_page5.Bind(wx.EVT_BUTTON, self.OnPage5)
		goto_page3.Bind(wx.EVT_BUTTON, self.OnPage3)

	def OnPage5(self, event):
		if not self.tc1.Value or not self.tc2.Value:
                	wx.MessageBox('Please fill out all entries', 'Incomplete', wx.OK | wx.ICON_ERROR)	
		elif self.tc1.Value != self.tc2.Value:
                	wx.MessageBox('Passwords do not match', 'Incomplete', wx.OK | wx.ICON_ERROR)	
		else:
			enc=stack.password.Enc()
			value = self.tc1.Value

			print self.sizer
			# encrypt the root password
			self.data.Kickstart_PrivateRootPassword = enc.enc_crypt(value)

			# mysql requires a sha(sha()) password
			self.data.Kickstart_PrivateSHARootPassword = enc.enc_shasha(value)

			# Wordpress requires a portable root password
			self.data.Kickstart_PrivatePortableRootPassword = enc.enc_portable(value)

			# Django requires a sha1 password in a slightly
			# different format
			self.data.Kickstart_PrivateDjangoRootPassword = enc.enc_django(value)

			# MD5 hash for Root password. Required for
			# things like Cloudstack
			self.data.Kickstart_PrivateMD5RootPassword = enc.enc_md5(value)

			# Display loading message
			#hbox2 = wx.BoxSizer(wx.HORIZONTAL)
			#png = wx.Image('/opt/stack/bin/cd.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			#cdBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
			#wait = wx.StaticText(self, label="Loading DVD pallets, please wait...")
			#hbox2.Add(cdBitmap, 0, wx.RIGHT, 10)
			#hbox2.Add(wait, 0, wx.RIGHT, 0)
			#self.sizer.Add(hbox2, pos=(4, 4), flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, border=20)

			# Resize the display to account for new message
			#self.SetSizerAndFit(self.sizer)

			wx.PostEvent(self.parent, PageChangeEvent(page=Page5))

	def OnPage3(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page3))

class Page5(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		sizer = wx.GridBagSizer(3, 1)

		#get the logo image
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#get the help image
		png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                helpBitmap1 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                helpBitmap2 = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.r1 = wx.RadioButton(self, label='Automated', pos=(10, 30), style=wx.RB_GROUP)
		self.r2 = wx.RadioButton(self, label='Manual', pos=(10, 50))

		gs = wx.GridSizer(2, 2, 5, 0)
		gs.AddMany([(self.r1), (helpBitmap1), (self.r2), (helpBitmap2)])

		#tooltip bubble
		helpBitmap1.SetToolTip(wx.ToolTip("The first disk on this machine will be partitioned in the " \
			"default manner. See the documentation for details on the default partitioning scheme."))
		helpBitmap2.SetToolTip(wx.ToolTip("You will be required to set all partitioning information for " \
			"this machine. A subsequent installation screen will allow you to enter your " \
			"partitioning information."))

		sizer.Add(gs, pos=(2, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#top label
		label = wx.StaticText(self, label='Partition Setup')
		sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#next button
		goto_page4 = wx.Button(self, label="Back")
		goto_page6 = wx.Button(self, label="Continue")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page4, 0, wx.LEFT, 20)
		hbox.Add(goto_page6, 0, wx.LEFT, 20)
		sizer.Add(hbox, pos=(3, 0), flag=wx.RIGHT|wx.BOTTOM, border=20)

		#set sizer
		sizer.AddGrowableCol(1)
		sizer.AddGrowableCol(2)
		self.SetSizerAndFit(sizer)

		#bind event to the next button
		goto_page4.Bind(wx.EVT_BUTTON, self.OnPage4)
		goto_page6.Bind(wx.EVT_BUTTON, self.OnPage6)

	def OnPage6(self, event):
		if self.r1.GetValue():
			self.data.partition = 'Automated'
			self.data.nukedisks = True
		elif self.r2.GetValue():
			self.data.partition = 'Manual'
		wx.PostEvent(self.parent, PageChangeEvent(page=Page6))

	def OnPage4(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page4))

class Page6(wx.Panel):

	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		sizer = wx.GridBagSizer(3, 2)

		#get the logo image
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#top label
		label = wx.StaticText(self, label='Pallets to Install')
		sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#box sizers
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		leftPanel = wx.Panel(self, -1)
		rightPanel = wx.Panel(self, -1)

		#list of dict for adding pallets by network
		self.pallets = []

		#right panel for list
		self.list1 = CheckListCtrl(rightPanel)
		self.list1.InsertColumn(0, 'Pallet Name', width = 140)
		self.list1.InsertColumn(1, 'Version')
		self.list1.InsertColumn(2, 'Id', width = 100)
		self.list1.InsertColumn(3, 'Network', width = 170)

		#check if CD is mounted and get list
		packages = []
		media = stack.media.Media()

		cdInfo = media.getCDInfo()
		disk_id = media.getId()
		print 'cd info: ' + str(cdInfo)
		print 'disk id: ' + str(disk_id)

		if cdInfo[1] == 'RHEL' or cdInfo[1] == 'CentOS':
			packages.append((cdInfo[1], cdInfo[4], disk_id))
		else:
			rolls = media.getRollsFromCD()
			for w in rolls:
				packages.append((w[0], w[1], disk_id))

		#populate list of rolls
		for i in packages:
			if i[0] == None:
				continue
			index = self.list1.InsertStringItem(sys.maxint, i[0])
			self.list1.SetStringItem(index, 1, i[1])
			self.list1.SetStringItem(index, 2, i[2])
			self.list1.SetStringItem(index, 3, '')

		#left panel for buttons
		sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
		des = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
		more = wx.Button(leftPanel, -1, 'Add Pallets', size=(100, -1))

		vbox.Add(sel, 15, wx.TOP, 0)
		vbox.Add(des, 15, wx.TOP, 5)
		vbox.Add(more, 15, wx.TOP, 5)

		leftPanel.SetSizer(vbox)

		hbox.Add(leftPanel, 15, wx.RIGHT, 20)
		hbox.Add(rightPanel)

		sizer.Add(hbox, pos=(2, 0), span=(1, 5), flag=wx.LEFT|wx.RIGHT, border=20)

		#bind button events
		sel.Bind(wx.EVT_BUTTON, self.OnSelectAll)
		des.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
		more.Bind(wx.EVT_BUTTON, self.OnAddPallets)

		#next buttons
		goto_page5 = wx.Button(self, label="Back")
		goto_page7 = wx.Button(self, label="Continue")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page5, 0, wx.LEFT, 280)
		hbox.Add(goto_page7, 0, wx.LEFT, 20)
		sizer.Add(hbox, pos=(3, 1), flag=wx.ALIGN_LEFT|wx.TOP, border=2)

		#set sizer
		sizer.AddGrowableCol(1)
		sizer.AddGrowableCol(2)
		self.SetSizerAndFit(sizer)

		#bind event to the next button
		goto_page5.Bind(wx.EVT_BUTTON, self.OnPage5)
		goto_page7.Bind(wx.EVT_BUTTON, self.OnPage7)

	def OnSelectAll(self, event):
		num = self.list1.GetItemCount()
		for i in range(num):
			self.list1.CheckItem(i)

	def OnDeselectAll(self, event):
		num = self.list1.GetItemCount()
		for i in range(num):
			self.list1.CheckItem(i, False)

	def OnAddPallets(self, event):
		dialog = AddPalletsDialog(None, title='Add Pallets', page=self)
		dialog.ShowModal()
		dialog.Destroy()

	def OnPage7(self, event):
		dvdrolls = []
		netrolls = []
		num = self.list1.GetItemCount()
		count = 0
		for i in range(num):
			if self.list1.IsChecked(i):
				n = str(self.list1.GetItem(i, 0).GetText())
				v = str(self.list1.GetItem(i, 1).GetText())
				d = str(self.list1.GetItem(i, 2).GetText())
				u = str(self.list1.GetItem(i, 3).GetText())
				o = {'name' : n, 'version' : v,'id' : d, 'url' :  u}

				#if no disk_id then assume it is a netroll
				if not d:
					netrolls.append(o)
				else:
					dvdrolls.append(o)
				count += 1

		if not count > 0:
                	wx.MessageBox('Please select which pallets to install', 'Incomplete', wx.OK | wx.ICON_ERROR)	
		else:
			self.data.dvdrolls = dvdrolls
			self.data.netrolls = netrolls
			wx.PostEvent(self.parent, PageChangeEvent(page=Page7))

	def OnPage5(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page5))

class AddPalletsDialog(wx.Dialog):
	def __init__(self, *args, **kw):
		super(AddPalletsDialog, self).__init__(*args, title=kw['title'])

		self.page = kw["page"]
		self.InitUI()
		self.SetSize((500, 200))

	def InitUI(self):

		#comment out the following to bypass 'add more pallets' from DVD

		#png = wx.Image('/opt/stack/bin/disk.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		#imageDisk = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		png = wx.Image('/opt/stack/bin/network.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		imageNetwork = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		helpImage = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

		#sizer = wx.GridBagSizer(4, 2)
		sizer = wx.GridBagSizer(3, 2)

		#header
		#label = wx.StaticText(self, label='Choose a method to load more pallets')
		#sizer.Add(label, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#dvd pallets
		#lb1 = wx.StaticText(self, label='Add more pallets with a CD/DVD')
		#dvdButtonEject = wx.Button(self, label='Eject')
		#dvdButtonLoad = wx.Button(self, label='Load')

		#vbox1 = wx.BoxSizer(wx.VERTICAL)
		#vbox1.Add(lb1)
		#hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		#hbox1.Add(dvdButtonEject, proportion=0, flag=wx.RIGHT|wx.TOP, border=10)
		#hbox1.Add(dvdButtonLoad, proportion=0, flag=wx.RIGHT|wx.TOP, border=10)
		#vbox1.Add(hbox1)

		#network pallets
		lb2 = wx.StaticText(self, label='Add pallets from a network')
		self.urlText = wx.TextCtrl(self, size=(410, -1))
		self.urlText.SetForegroundColour(wx.BLACK)
		self.urlText.SetBackgroundColour(wx.WHITE)

		urlButton = wx.Button(self, label='Load')
		cancelButton = wx.Button(self, label='Cancel')

		helpImage.SetToolTip(wx.ToolTip("Enter the URL of the pallets server.\nLoading will query the " +\
			"server and have all pallets available to be displayed."))

		vbox2 = wx.BoxSizer(wx.VERTICAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(lb2)
		hbox3.Add(helpImage, 0, wx.LEFT, 10)
		vbox2.Add(hbox3)
		vbox2.Add(self.urlText, proportion=0, flag=wx.TOP, border=10)

		#buttons
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(cancelButton, 0, wx.LEFT, 20)
		hbox2.Add(urlButton, 0, wx.LEFT, 20)

		fgs = wx.FlexGridSizer(2, 2, 9, 25)
		#fgs.AddMany([(imageDisk), (vbox1), (imageNetwork, 0, wx.TOP, 20), (vbox2, 0, wx.TOP, 20)])
		fgs.AddMany([(imageNetwork, 0, wx.TOP, 20), (vbox2, 0, wx.TOP, 20)])
		sizer.Add(fgs, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		sizer.Add(hbox2, pos=(2, 1), span=(1, 5), flag=wx.ALIGN_RIGHT|wx.RIGHT, border=20)

		#close button
		#cancelButton = wx.Button(self, label='Done')
		#sizer.Add(cancelButton, pos=(3, 0), flag=wx.LEFT|wx.BOTTOM|wx.TOP, border=20)

		#set sizer
		sizer.AddGrowableCol(1)
		sizer.AddGrowableCol(2)
		self.SetSizerAndFit(sizer)

		#bind events
		cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
		#dvdButtonEject.Bind(wx.EVT_BUTTON, self.OnDVDEject)
		#dvdButtonLoad.Bind(wx.EVT_BUTTON, self.OnDVDLoad)
		urlButton.Bind(wx.EVT_BUTTON, self.OnUrlLoad)

	def OnUrlLoad(self, event):
		try:
			if not self.urlText.Value:
				wx.MessageBox('Please enter a URL to the location of pallets', 'Incomplete', \
					 wx.OK | wx.ICON_ERROR)
                        	return
			else:
				url = self.urlText.Value
				if url.find("http://") != 0:
					url = "http://" + url
				if not url.find("/install/pallets/") > 0:
					url = url.rstrip("//")
					url = url + "/install/pallets/"

				# Call boss_get_pallet_info.py to download pallet
				# information from network.
				p = subprocess.Popen(
					['/opt/stack/bin/boss_get_pallet_info.py', url],
					stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				o, e = p.communicate()
				rc = p.wait()

				if rc == 0:
					pallets = pickle.loads(o)
					for p in pallets:
						index = self.page.list1.InsertStringItem(sys.maxint, p['name'])
						self.page.list1.SetStringItem(index, 1, p['version'])
						self.page.list1.SetStringItem(index, 2, p['id'])
						self.page.list1.SetStringItem(index, 3, p['url'])
						self.page.pallets.append(p)
				else:
					print e
					wx.MessageBox('Sorry, cannot recognize the URL', 'Invalid URL', wx.OK | wx.ICON_ERROR)
					return

				self.Destroy()
		except:
			print traceback.format_exc()
			wx.MessageBox('Sorry, cannot recognize the URL', 'Invalid URL', wx.OK | wx.ICON_ERROR)
			return

	def OnDVDEject(self, event):
		media = stack.media.Media()
		media.umountCD()
		media.ejectCD()

	def OnDVDLoad(self, event):
		media = stack.media.Media()
		media.mountCD()

		#get more pallets
		packages = []

		rolls = media.getRollsFromCD()
		disk_id = media.getId()
		for w in rolls:
			packages.append((w[0], w[1], disk_id))

		for i in packages:
			if i[0] == None:
				continue
			index = self.page.list1.InsertStringItem(sys.maxint, i[0])
			self.page.list1.SetStringItem(index, 1, i[1])
			self.page.list1.SetStringItem(index, 2, i[2])
			self.page.list1.SetStringItem(index, 3, '')

	def OnClose(self, event):
		self.Destroy()

class Page7(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		sizer = wx.GridBagSizer(3, 4)

		#get the logo image
                png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                imageBitmap = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
                sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#top label
		lb = wx.StaticText(self, label='Cluster Summary')
		sizer.Add(lb, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#display summary data
		summaryStr = 'Cluster Name: \t\t\t\t' + data.Info_ClusterName + '\n' + \
				'Fully Qualified Domain Name: \t' + data.Kickstart_PublicHostname + '\n' + \
				'Email: \t\t\t\t\t\t' + data.Info_ClusterContact + '\n' + \
				'Timezone: \t\t\t\t\t' + data.Kickstart_Timezone + '\n' + \
				'Public Device: \t\t\t\t' + data.Kickstart_PublicInterface + '\n' + \
				'Public IP: \t\t\t\t\t' + data.Kickstart_PublicAddress + '\n' + \
				'Public Netmask: \t\t\t\t' + data.Kickstart_PublicNetmask + '\n' + \
				'Public Gateway: \t\t\t\t' + data.Kickstart_PublicGateway + '\n' + \
				'Public DNS Servers: \t\t\t' + data.Kickstart_PublicDNSServers + '\n' + \
				'Private Device: \t\t\t\t' + data.Kickstart_PrivateInterface + '\n' + \
				'Private IP: \t\t\t\t\t' + data.Kickstart_PrivateAddress + '\n' + \
				'Private Netmask: \t\t\t\t' + data.Kickstart_PrivateNetmask + '\n' + \
				'Partition: \t\t\t\t\t' + data.partition + '\n'

		#display list of pallets
		pstr = ''
		for w in self.data.dvdrolls:
			pstr += '\t\t\t\t\t\t\t' + w['name'] + '\n'

		for w in self.data.netrolls:
			pstr += '\t\t\t\t\t\t\t' + w['name'] + '\n'
		summaryStr += 'Pallets to Install: \n' + pstr

		tc = wx.TextCtrl(self, -1, summaryStr, size=(595, 300),style=wx.TE_MULTILINE|wx.TE_READONLY)
		sizer.Add(tc, pos=(2, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#next button
		goto_page6 = wx.Button(self, label="Back")
		goto_page8 = wx.Button(self, label="Install")

		hbox = wx.BoxSizer(wx.HORIZONTAL)
                hbox.Add(goto_page6, 0, wx.RIGHT, 20)
                hbox.Add(goto_page8)
                sizer.Add(hbox, pos=(3, 0), flag=wx.LEFT|wx.BOTTOM, border=20)

                #set sizer
                self.SetSizerAndFit(sizer)

		#bind event to the next button
		goto_page6.Bind(wx.EVT_BUTTON, self.OnPage6)
		goto_page8.Bind(wx.EVT_BUTTON, self.OnPage8)

	def OnPage8(self, event):

		#write site.attrs
		f = open('/tmp/site.attrs', 'w')
		members = [attr for attr in dir(self.data) if not callable(attr) and not \
			attr.startswith("__") and not attr == 'devices' and not \
			attr == 'dvdrolls' and not attr == 'netrolls' and not attr == 'partition']
		for w in members:
			v = getattr(self.data, w)
			f.write(str(w) + ":" + str(v) + os.linesep)
		f.close()
		wx.PostEvent(self.parent, PageChangeEvent(page=finish))

		#create xml elements and write rolls.xml
		#write rolls from dvd
		rolls = Element('rolls')
		for w in self.data.dvdrolls:
			roll = SubElement(rolls, 'roll', \
				name=w['name'], \
				version=w['version'], \
				arch='x86_64', \
				url='http://127.0.0.1/mnt/cdrom/', \
				diskid=w['id'])

		#write rolls from network
		for w in self.data.netrolls:
			roll = SubElement(rolls, 'roll', \
				name=w['name'], \
				version=w['version'], \
				arch='x86_64', \
				url=w['url'], \
				diskid='')
		tree = ElementTree(rolls)
		tree.write('/tmp/rolls.xml')

		#write user_partition_info if manual
		if self.data.partition == 'Manual':
			f = open('/tmp/user_partition_info', 'w+')
			f.write('stack manual')
			f.close()

	def OnPage6(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page6))

def finish(parent, data):
	wx.GetApp().ExitMainLoop()


class Boss(wx.Frame):
	def __init__(self, parent, title):
		super(Boss, self).__init__(parent, title=title, size=(675, 500))
		self.data = Data()
		self.current_page = None

		self.Bind(EVT_PAGE_CHANGE, self.OnPageChange)
		wx.PostEvent(self, PageChangeEvent(page=Page1))

	def OnPageChange(self, event):
		page = event.page(self, self.data)
		if page == None:
			return
		if self.current_page:
			self.current_page.Destroy()
		self.current_page = page
		page.Layout()
		page.Fit()
		page.Refresh()


#
# make sure the DVD is mounted
#
cmd = 'mkdir -p /mnt/cdrom ; mount /dev/cdrom /mnt/cdrom'
os.system(cmd)

app = wx.App()
app.TopWindow = Boss(None, title='stacki Installation')
app.TopWindow.Show()
app.MainLoop()
