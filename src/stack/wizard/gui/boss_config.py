#!/opt/stack/bin/python
from __future__ import print_function
import os
import subprocess
import stack.media
import stack.wizard

import sys
import traceback
import urllib2
import pickle

#
# set network config and snack flags
#
config_net = True
noX = False
no_partition = False

for s in sys.argv:
	if s == '--no-net-reconfig':
		config_net = False
	elif s == '--noX':
		noX = True
	elif s == '--no-partition':
		no_partition = True


if not os.environ.has_key('DISPLAY'):
	noX = True

print('Set network during boss_config: ' + str(config_net))
print('Use snack installation instead of wx: ' + str(noX))
print('Disable partitioning: ' + str(no_partition))

#
# make sure the installation ISO is mounted on /mnt/cdrom. it could be a
# USB stick or DVD
#
cmdline = open('/proc/cmdline', 'r')
cmdargs = cmdline.readline()
cmdline.close()

#
# if this is a USB install, then we'll see a kernel command line parameter
# that looks like:
#
#	inst.stage2=hd:sda1:/
#
# and we want to parse out the disk device (e.g., 'sda1')
#

device = None
for cmdarg in cmdargs.split():
	if cmdarg.startswith('inst.stage2='):
		b = cmdarg.split('=')
		c = b[1].split(':')
		if len(c) > 1 and c[0] == 'hd':
			device = c[1]
			break

		# Create /mnt/cdrom if it doesn't exist
		if not os.path.exists('/mnt/cdrom'):
			os.makedirs('/mnt/cdrom')
		cmd = 'mount /dev/%s /mnt/cdrom' % device
		os.system(cmd)

#try to get wxpython
try:
	import wx
except ImportError:
	noX = True

if noX:
	p = subprocess.Popen(["/opt/stack/bin/boss_config_snack.py"] + sys.argv[1:])
	rc = p.wait()
	sys.exit(rc)


import wx.lib.newevent
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin


def createLogo(panel):
	png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
	return wx.StaticBitmap(panel, -1, png, (10, 5),
		(png.GetWidth(), png.GetHeight()))

def createHelp(panel, text):
	png = wx.Image('/opt/stack/bin/help.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
	bitmap = wx.StaticBitmap(panel, -1, png, (10, 5),
		(png.GetWidth(), png.GetHeight()))
	bitmap.SetToolTip(wx.ToolTip(text))
	return bitmap

def createSizer(v, h, page, title):
	sizer = wx.GridBagSizer(v, h)
	logoBitmap = createLogo(page)
	sizer.Add(logoBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)
	label = wx.StaticText(page, label=title)
	sizer.Add(label, pos=(1, 0), span=(1, 5),
		flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)
	return sizer

def createContinue(page, func):
	btn = wx.Button(page, label="Continue")
	btn.Bind(wx.EVT_BUTTON, func)
	return btn

def createButton(page, func, label):
	btn = wx.Button(page, label=label)
	btn.Bind(wx.EVT_BUTTON, func)
	return btn

def createBack(page, func):
	btn = wx.Button(page, label="Back")
	btn.Bind(wx.EVT_BUTTON, func)
	return btn

def createComboBox(page, list, label, value):
	if label == "Timezone":
		cb = wx.ComboBox(page, value=value, pos=(50, 30), size=(300, -1),
			choices=list, style=wx.CB_READONLY)
	else:
		cb = wx.ComboBox(page, value=value, pos=(50, 30), size=(200, -1),
			choices=list, style=wx.CB_READONLY)
	cb.SetForegroundColour(wx.BLACK)
	cb.SetBackgroundColour(wx.WHITE)
	return cb

def createRadio(page, label, text, style):
	if style:
		r = wx.RadioButton(page, label=label, pos=(10, 30), style=style)	
	else:
		r = wx.RadioButton(page, label=label, pos=(10, 30))	
	help = createHelp(page, text)
	return (r, help)

def createTextCtrl(page, value, style):
	if style:
		tc = wx.TextCtrl(page, value=value, style=style)
	else:
		tc = wx.TextCtrl(page, value=value)
	tc.SetForegroundColour(wx.BLACK)
	tc.SetBackgroundColour(wx.WHITE)
	return tc

def setSizer(page, sizer):
	sizer.AddGrowableCol(1)
	sizer.AddGrowableRow(2)
	page.SetSizerAndFit(sizer)

def createCb(page, label, text, list, value):
	lb = wx.StaticText(page, label=label)
	help = createHelp(page, text)
	cb = createComboBox(page, list, label, value)
	return (lb, help, cb)

def createTc(page, label, text, value, style):
	lb = wx.StaticText(page, label=label)
	help = createHelp(page, text)
	tc = createTextCtrl(page, value, style)
	return (lb, help, tc)


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1,
			style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)	


class Page1(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#create layout
		sizer = createSizer(4, 1, self, "Begin Installation")

		#map image
		bitmap = wx.Bitmap('/opt/stack/bin/earthmap.bmp')
		img_w = bitmap.GetWidth()
		img_h = bitmap.GetHeight()
		self.control = wx.StaticBitmap(self, -1, bitmap, (10, 5),
			(img_w, img_h))

		self.hq = round(img_w / 2)
		self.vq = round(img_h / 2)

		#get list of timezones and cordinates
		cities = []
		self.cordinates = []

		for line in open('/opt/stack/bin/timezones.txt'):
			line = line.replace('\n', '')
			line = filter(None, line.split('\t'))
			cord = line[1].split(', ')
			cities.append(line[0])
			self.cordinates.append((line[0], cord[0], cord[1]))

		#get label, help and combo-box for timezones
		lb, img, self.cb = createCb(self, "Timezone", 
			"Select the city or nearest city in the\ntimezone " + \
			"of this cluster", cities, data.get('Kickstart_Timezone'))

		#bind update map function to combobox
		self.cb.Bind(wx.EVT_COMBOBOX, self.UpdateMap)

		#call update map if value has been set
		self.UpdateMap(wx.EVT_COMBOBOX)

		#continue button
		goto_page2 = createContinue(self, self.OnPage2)

		#put elements into form
		fgs = wx.FlexGridSizer(1, 4, 9, 25)
		fgs.AddMany([lb, img, (self.cb, 1, wx.EXPAND), goto_page2])

		#add to sizer
		sizer.Add(fgs, pos=(2, 0), span=(1, 1),
			flag=wx.LEFT|wx.BOTTOM, border=20)
		sizer.Add(self.control, pos=(3,0), flag=wx.LEFT|wx.BOTTOM, border=20)

		#apply sizer to the page
		self.SetSizerAndFit(sizer)

	def UpdateMap(self, event):

		#half dimensions of bitmap
		img_w = self.hq
		img_h = self.vq

		#search tuple for coridinates
		selected = str(self.cb.Value)
		if selected:
			for city, ln, la in self.cordinates:
				if city == selected:
					lon = ln
					lat = la
					continue

			#determine which quadrant to use
			if lon.find('N') > -1:
				north = True
			else:
				north = False

			if lat.find('W') > -1:
				west = True
			else:
				west = False

			#get longitude and latitude
			lon = float(lon.split(' ')[0])
			lat = float(lat.split(' ')[0])

			#translate longitude to y
			perc = float(lon / 90)
			offset = round(perc * img_h)
			if north:
				y = img_h - offset
			else:
				y = img_h + offset

			#translate latitude to x
			perc = float(lat / 180)
			offset = round(perc * img_w)
			if west:
				x = img_w - offset
			else:
				x = img_w + offset

			#draw new bitmap
			bitmap = wx.Bitmap('/opt/stack/bin/earthmap.bmp')
			self.dc = wx.MemoryDC(bitmap)
			self.dc.SetPen(wx.Pen(wx.RED, 1))
			self.dc.CrossHair(x, y)
			self.control.SetBitmap(bitmap)

	def OnPage2(self, event):
		validated, message, title = \
			self.data.validateTimezone(str(self.cb.Value))
		if not validated:
			wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)	
		else:
			wx.PostEvent(self.parent, PageChangeEvent(page=Page2))

class Page2(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#create layout
		sizer = createSizer(3, 4, self, "Network")

		#get list of interfaces
		devices = data.getDevices()
		list = []
		for d in devices:
			list.append(d)
		list = sorted(list)

		#create labels, bitmaps and inputs
		fqdn, helpBitmap0, self.tc0 = createTc(self,
			"Fully Qualified Host Name", \
			"This must be the fully-qualified domain name\n" + \
			"(e.g., dev.stacki.com)", \
			data.get('Info_FQDN'), None)
		d, helpBitmap1, self.cb = createCb(self, \
			"Devices", "This is the interface that connects to the " + \
			"network that will be used by the frontend to install backend hosts", list,
			data.get('Kickstart_PrivateInterface'))
		ip, helpBitmap2, self.tc1 = createTc(self, "IP",
			"IP address for the device",
			data.get('Kickstart_PrivateAddress'), None)
		mask, helpBitmap3, self.tc2 = createTc(self, "Netmask",
			"Netmask for the device", \
			data.get('Kickstart_PrivateNetmask'), None)
		gw, helpBitmap4, self.tc3 = createTc(self, "Gateway",
			"IP address of your public gateway", \
			data.get('Kickstart_PrivateGateway'), None)
		dns, helpBitmap5, self.tc4 = createTc(self, "DNS Servers",
			"Supply a comma separated list of your DNS servers " + \
			"if you have more than one",
			data.get('Kickstart_PrivateDNSServers'), None)

		#put elements into form
		fgs = wx.FlexGridSizer(6, 3, 9, 25)
		fgs.AddMany([
			(fqdn), (helpBitmap0), (self.tc0, 1, wx.EXPAND),
			(d), (helpBitmap1), (self.cb, 1, wx.EXPAND),
			(ip), (helpBitmap2), (self.tc1, 1, wx.EXPAND),
			(mask), (helpBitmap3), (self.tc2, 1, wx.EXPAND),
			(gw), (helpBitmap4), (self.tc3, 1, wx.EXPAND),
			(dns), (helpBitmap5), (self.tc4, 1, wx.EXPAND)
		])
		fgs.AddGrowableCol(2, 2)
		sizer.Add(fgs, pos=(2, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#back and continue buttons
		goto_page1 = createBack(self, self.OnPage1)
		goto_page4 = createContinue(self, self.OnPage4)

		#create box for navigation and add to sizer
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page1, 0, wx.RIGHT, 20)
		hbox.Add(goto_page4)
		sizer.Add(hbox, pos=(3, 4), flag=wx.RIGHT|wx.BOTTOM, border=20)

		#apply sizer to the page
		setSizer(self, sizer)

	def OnPage4(self, event):
		fqdn = str(self.tc0.Value)
		tup = (str(self.tc0.Value), str(self.cb.Value), str(self.tc1.Value),
			str(self.tc2.Value), str(self.tc3.Value), str(self.tc4.Value))

		#check the FQDN for appliance names
		validated, message, title = self.data.validateDomain(fqdn)
		if not validated:
			wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)	
		else:
			#check for valid network config
			validated, message, title = self.data.validateNetwork(tup, config_net)
			if not validated:
				wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)	
			else:
				#proceed to next page
				wx.PostEvent(self.parent, PageChangeEvent(page=Page4))

	def OnPage1(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page1))


class Page4(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#create layout
		sizer = createSizer(2, 4, self, "Password")

		#create labels, bitmaps and inputs
		pass1, helpBitmap1, self.tc1 = createTc(self, "Password", \
			"The root password for this cluster", "", wx.TE_PASSWORD)
		pass2, helpBitmap2, self.tc2 = createTc(self, "Confirm Password", \
			"Confirm your password", "", wx.TE_PASSWORD)

		#put elements into form
		fgs = wx.FlexGridSizer(3, 3, 9, 25)
		fgs.AddMany([(pass1), (helpBitmap1), (self.tc1, 1, wx.EXPAND),
			(pass2), (helpBitmap2), (self.tc2, 1, wx.EXPAND)])
		fgs.AddGrowableCol(2, 2)
		sizer.Add(fgs, pos=(2, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#continue and back button
		goto_page5 = createContinue(self, self.OnPage5)
		goto_page2 = createBack(self, self.OnPage2)

		#create box for navigation and add to sizer
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page2, 0, wx.RIGHT, 20)
		hbox.Add(goto_page5, 0, flag=wx.ALIGN_RIGHT)
		sizer.Add(hbox, pos=(3, 4), flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM,
			border=20)

		#apply sizer to page
		setSizer(self, sizer)

	def OnPage5(self, event):
		validated, message, title = \
			self.data.validatePassword(self.tc1.Value, self.tc2.Value)
		if not validated:
			wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)	
		else:
			if not no_partition:
				wx.PostEvent(self.parent, PageChangeEvent(page=Page5))
			else:
				wx.PostEvent(self.parent, PageChangeEvent(page=Page6))

	def OnPage2(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page2))

class Page5(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#create layout
		sizer = createSizer(3, 1, self, "Partition")

		#create radio buttons
		txt1 = "The first disk on this machine will be partitioned in the " + \
			"default manner. See the documentation for details on the " + \
			"default partitioning scheme."
		txt2 = "You will be required to set all partitioning information " + \
			"for this machine. A subsequent installation screen will " + \
			"allow you to enter your partitioning information."

		self.r1, img1 = createRadio(self, "Automated", txt1, wx.RB_GROUP)
		self.r2, img2 = createRadio(self, "Manual", txt2, None)

		#put elements into form
		gs = wx.GridSizer(2, 2, 5, 0)
		gs.AddMany([(self.r1), (img1), (self.r2), (img2)])
		sizer.Add(gs, pos=(2, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=20)

		#continue and back button
		goto_page4 = createBack(self, self.OnPage4)
		goto_page6 = createContinue(self, self.OnPage6)

		#create box for navigation and add to sizer
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page4, 0, wx.LEFT, 20)
		hbox.Add(goto_page6, 0, wx.LEFT, 20)
		sizer.Add(hbox, pos=(3, 0), flag=wx.RIGHT|wx.BOTTOM, border=20)

		#apply sizer to page
		setSizer(self, sizer)

	def OnPage6(self, event):

		if self.r1.GetValue():
			partition = 'Automated'
		elif self.r2.GetValue():
			partition = 'Manual'

		validated, message, title = self.data.validatePartition(partition)
		if not validated:
			wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)
		else:
			wx.PostEvent(self.parent, PageChangeEvent(page=Page6))

	def OnPage4(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page4))

class Page6(wx.Panel):

	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#create layout
		sizer = createSizer(3, 2, self, "Pallets to Install")

		#right panel for list
		rightPanel = wx.Panel(self, -1)
		self.list1 = CheckListCtrl(rightPanel)
		self.list1.InsertColumn(0, 'Pallet Name', width = 140)
		self.list1.InsertColumn(1, 'Version')
		self.list1.InsertColumn(2, 'Release')
		self.list1.InsertColumn(3, 'Id', width = 100)
		self.list1.InsertColumn(4, 'Network', width = 170)

		#keep track of loading pallets
		self.pallets = []

		#get pallets from pallets
		packages = data.getDVDPallets()

		#populate list of rolls
		for idx, i in enumerate(packages):
			if i[0] == None:
				continue
			index = self.list1.InsertStringItem(sys.maxint, i[0])
			self.list1.SetStringItem(index, 1, i[1])
			self.list1.SetStringItem(index, 2, i[2])
			self.list1.SetStringItem(index, 3, i[3])
			self.list1.SetStringItem(index, 4, '')

			# By default select the pallet
			self.list1.CheckItem(idx)

		#left panel for buttons
		leftPanel = wx.Panel(self, -1)
		sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
		des = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
		more = wx.Button(leftPanel, -1, 'Add Pallets', size=(100, -1))

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(sel, 15, wx.TOP, 0)
		vbox.Add(des, 15, wx.TOP, 5)
		vbox.Add(more, 15, wx.TOP, 5)

		leftPanel.SetSizer(vbox)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(leftPanel, 15, wx.RIGHT, 20)
		hbox.Add(rightPanel)

		sizer.Add(hbox, pos=(2, 0), span=(1, 5),
			flag=wx.LEFT|wx.RIGHT, border=20)

		#bind button events
		sel.Bind(wx.EVT_BUTTON, self.OnSelectAll)
		des.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
		more.Bind(wx.EVT_BUTTON, self.OnAddPallets)

		#continue and back buttons
		goto_page5 = createBack(self, self.OnPage5)
		goto_page7 = createContinue(self, self.OnPage7)

		#create box for navigation and add to sizer
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page5, 0, wx.LEFT, 280)
		hbox.Add(goto_page7, 0, wx.LEFT, 20)
		sizer.Add(hbox, pos=(3, 1), flag=wx.ALIGN_LEFT|wx.TOP, border=2)

		#apply sizer to page
		setSizer(self, sizer)

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
		for i in range(num):
			if self.list1.IsChecked(i):
				name = str(self.list1.GetItem(i, 0).GetText())
				version = str(self.list1.GetItem(i, 1).GetText())
				release = str(self.list1.GetItem(i, 2).GetText())
				diskid = str(self.list1.GetItem(i, 3).GetText())
				url = str(self.list1.GetItem(i, 4).GetText())

				o = {'name' : name, 'version' : version,
					'release' : release, 'id' : diskid,
					'url' : url}

				#if no diskid then assume it is a netroll
				if not diskid:
					netrolls.append(o)
				else:
					dvdrolls.append(o)

		validated, message, title = \
			self.data.validatePallets(dvdrolls, netrolls)
		if not validated:
			wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)
		else:
			wx.PostEvent(self.parent, PageChangeEvent(page=Page7))

	def OnPage5(self, event):
		if not no_partition:
			wx.PostEvent(self.parent, PageChangeEvent(page=Page5))
		else:
			wx.PostEvent(self.parent, PageChangeEvent(page=Page4))

class AddPalletsDialog(wx.Dialog):

	def __init__(self, *args, **kw):
		super(AddPalletsDialog, self).__init__(*args, title=kw['title'])

		self.current_dialog = None
		self.SetSize((500, 200))
		self.page = kw['page']

		self.Bind(EVT_DIALOG_CHANGE, self.OnDialogChange)
		wx.PostEvent(self, DialogChangeEvent(dialog=DialogSelect))

	def OnDialogChange(self, event):
		dialog = event.dialog(self, self.page)
		if dialog == None:
			return
		if self.current_dialog:
			self.current_dialog.Destroy()
		self.current_dialog = dialog
		dialog.Layout()
		dialog.Fit()
		dialog.Refresh()

class DialogSelect(wx.Panel):

	def __init__(self, parent, page):
		wx.Panel.__init__(self, parent)
		self.parent = parent

		png = wx.Image('/opt/stack/bin/basket_add.png',
			wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		imageDisk = wx.StaticBitmap(self, -1, png, (10, 5),
			(png.GetWidth(), png.GetHeight()))

		helpImage = createHelp(self, "Choose DVD if you have another disk of pallets to install. " + \
			"Choose network if you have pallets at a remote network location with a provided URL.")

		#create sizer
		sizer = wx.GridBagSizer(3, 2)

		#create label and text input
		lb = wx.StaticText(self, label='Select a method to add more pallets to the list')

		#create buttons
		dvdButton = createButton(self, self.OnDVD, "DVD")
		urlButton = createButton(self, self.OnNetwork, "Network")

		#create box for input url
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(lb)
		hbox.Add(helpImage, 0, wx.LEFT, 10)
		vbox.Add(hbox)

		#create box for action buttons
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(dvdButton, 0, wx.LEFT, 20)
		hbox2.Add(urlButton, 0, wx.LEFT, 20)

		#add to form
		fgs = wx.FlexGridSizer(2, 2, 9, 25)
		fgs.AddMany([(imageDisk, 0, wx.TOP, 20), (vbox, 0, wx.TOP, 20)])
		sizer.Add(fgs, pos=(1, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		sizer.Add(hbox2, pos=(2, 1), span=(1, 5),
			flag=wx.ALIGN_RIGHT|wx.RIGHT, border=20)

		#apply sizer to the dialog
		setSizer(self, sizer)

	def OnNetwork(self, event):
		wx.PostEvent(self.parent, DialogChangeEvent(dialog=DialogNetwork))

	def OnDVD(self, event):
		#unmount and eject
		media = stack.media.Media()
		media.umountCD()
		media.ejectCD()

		wx.PostEvent(self.parent, DialogChangeEvent(dialog=DialogDVDLoad))

class DialogNetwork(wx.Panel):

	def __init__(self, parent, page):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.page = page

		png = wx.Image('/opt/stack/bin/network.png',
			wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		imageNetwork = wx.StaticBitmap(self, -1, png, (10, 5),
			(png.GetWidth(), png.GetHeight()))

		helpImage = createHelp(self, "Enter the URL of the pallets " + \
			"server.\nLoading will query the server and have all " + \
			"pallets available to be displayed.")

		#create sizer
		sizer = wx.GridBagSizer(3, 2)

		#create label and text input
		lb = wx.StaticText(self, label='Add pallets from a network')
		self.urlText = wx.TextCtrl(self, size=(410, -1))
		self.urlText.SetForegroundColour(wx.BLACK)
		self.urlText.SetBackgroundColour(wx.WHITE)

		#create buttons
		urlButton = createButton(self, self.OnUrlLoad, "Load")
		cancelButton = createButton(self, self.OnClose, "Cancel")

		#create box for input url
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(lb)
		hbox.Add(helpImage, 0, wx.LEFT, 10)
		vbox.Add(hbox)
		vbox.Add(self.urlText, proportion=0, flag=wx.TOP, border=10)

		#create box for action buttons
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(cancelButton, 0, wx.LEFT, 20)
		hbox2.Add(urlButton, 0, wx.LEFT, 20)

		#add to form
		fgs = wx.FlexGridSizer(2, 2, 9, 25)
		fgs.AddMany([(imageNetwork, 0, wx.TOP, 20), (vbox, 0, wx.TOP, 20)])
		sizer.Add(fgs, pos=(1, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		sizer.Add(hbox2, pos=(2, 1), span=(1, 5),
			flag=wx.ALIGN_RIGHT|wx.RIGHT, border=20)

		#apply sizer to the dialog
		setSizer(self, sizer)

	def OnClose(self, event):
		self.parent.Destroy()

	def OnUrlLoad(self, event):
		if not self.urlText.Value:
			wx.MessageBox('Please enter a URL to the location ' + \
				'of pallets', 'Incomplete',
				wx.OK | wx.ICON_ERROR)
			return
		else:
			try:
				url = self.urlText.Value
				if url.find("http://") != 0:
					url = "http://" + url
				if not url.find("/install/pallets/") > 0:
					url = url.rstrip("//")
					url = url + "/install/pallets/"

				#
				# Call boss_get_pallet_info.py to download pallet
				# information from network.
				#
				p = subprocess.Popen(
					['/opt/stack/bin/boss_get_pallet_info.py',
					url],
					stdout = subprocess.PIPE, stderr = \
						subprocess.PIPE)
				o, e = p.communicate()
				rc = p.wait()

				if rc == 0:
					pallets = pickle.loads(o)
					for p in pallets:
						index = \
							self.page.list1.InsertStringItem(
								sys.maxint, p['name'])
						self.page.list1.SetStringItem(index,
							1, p['version'])
						self.page.list1.SetStringItem(index,
							2, p['release'])
						self.page.list1.SetStringItem(index,
							3, p['id'])
						self.page.list1.SetStringItem(index,
							4, p['url'])
						self.page.pallets.append(p)
				else:
					print(e)
					wx.MessageBox('Sorry, cannot recognize ' + \
						'the URL', 'Invalid URL',
						wx.OK | wx.ICON_ERROR)
					return

				self.parent.Destroy()

			except OSError as err:
				if "No such file" in str(err):
					wx.MessageBox('Missing a file for installation', \
						'File Missing', wx.OK | wx.ICON_ERROR)
				else:
					wx.MessageBox('OS Error: %s' % err, \
						'OS Error', wx.OK | wx.ICON_ERROR)
				return

# Don't catch the exception so we can debug messed
# up build environments
#
#		except:
#			wx.MessageBox('Sorry, cannot recognize the URL',
#				'EXCEPTION', wx.OK | wx.ICON_ERROR)
#			return


class DialogDVDEject(wx.Panel):

	def __init__(self, parent, page):
		wx.Panel.__init__(self, parent)
		self.parent = parent

		png = wx.Image('/opt/stack/bin/disk.png',
			wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		imageDisk = wx.StaticBitmap(self, -1, png, (10, 5),
			(png.GetWidth(), png.GetHeight()))

		helpImage = createHelp(self, "This disk is not the current installation disk but another disk with extra pallets that you might have")

		#create sizer
		sizer = wx.GridBagSizer(3, 2)

		#create label and text input
		lb = wx.StaticText(self, label='Add more pallets from another DVD')

		#create buttons
		closeButton = createButton(self, self.OnClose, "Cancel")
		startButton = createButton(self, self.OnBegin, "Start")

		#create box for input url
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(lb)
		hbox.Add(helpImage, 0, wx.LEFT, 10)
		vbox.Add(hbox)

		#create box for action buttons
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(closeButton, 0, wx.LEFT, 20)
		hbox2.Add(startButton, 0, wx.LEFT, 20)

		#add to form
		fgs = wx.FlexGridSizer(2, 2, 9, 25)
		fgs.AddMany([(imageDisk, 0, wx.TOP, 20), (vbox, 0, wx.TOP, 20)])
		sizer.Add(fgs, pos=(1, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		sizer.Add(hbox2, pos=(2, 1), span=(1, 5),
			flag=wx.ALIGN_RIGHT|wx.RIGHT, border=20)

		#apply sizer to the dialog
		setSizer(self, sizer)

	def OnBegin(self, event):
		media = stack.media.Media()
		media.umountCD()
		media.ejectCD()
		wx.PostEvent(self.parent, DialogChangeEvent(dialog=DialogDVDLoad))

	def OnClose(self, event):
		self.parent.Destroy()


class DialogDVDLoad(wx.Panel):

	def __init__(self, parent, page):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.page = page

		png = wx.Image('/opt/stack/bin/disk.png',
			wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		imageDisk = wx.StaticBitmap(self, -1, png, (10, 5),
			(png.GetWidth(), png.GetHeight()))

		helpImage = createHelp(self, "Loading will not install pallets but only make them available to select")

		#create sizer
		sizer = wx.GridBagSizer(3, 2)

		#create label and text input
		lb = wx.StaticText(self, label='Please insert the DVD to load pallets')

		#create buttons
		closeButton = createButton(self, self.OnClose, "Cancel")
		loadButton = createButton(self, self.OnDVDLoad, "Load")

		#create box for input url
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(lb)
		hbox.Add(helpImage, 0, wx.LEFT, 10)
		vbox.Add(hbox)

		#create box for action buttons
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(closeButton, 0, wx.LEFT, 20)
		hbox2.Add(loadButton, 0, wx.LEFT, 20)

		#add to form
		fgs = wx.FlexGridSizer(2, 2, 9, 25)
		fgs.AddMany([(imageDisk, 0, wx.TOP, 20), (vbox, 0, wx.TOP, 20)])
		sizer.Add(fgs, pos=(1, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)
		sizer.Add(hbox2, pos=(2, 1), span=(1, 5),
			flag=wx.ALIGN_RIGHT|wx.RIGHT, border=20)

		#apply sizer to the dialog
		setSizer(self, sizer)

	def OnDVDLoad(self, event):

		#mount cdrom
		cmd = 'mount /dev/cdrom /mnt/cdrom'
		os.system(cmd)

		#get pallets from DVD
		packages = self.page.data.getDVDPallets()
		for i in packages:
			if i[0] == None:
				continue
			index = self.page.list1.InsertStringItem(sys.maxint, i[0])
			self.page.list1.SetStringItem(index, 1, i[1])
			self.page.list1.SetStringItem(index, 2, i[2])
			self.page.list1.SetStringItem(index, 3, '')

		wx.PostEvent(self.parent, DialogChangeEvent(dialog=DialogDVDEject))
		self.parent.Destroy()

	def OnClose(self, event):
		self.parent.Destroy()


class Page7(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.data = data

		#create sizer
		sizer = createSizer(3, 4, self, "Cluster Summary")

		#display summary data
		summaryStr = data.generateSummary()

		#insert text to display
		tc = wx.TextCtrl(self, -1, summaryStr, size=(595, 300),
			style=wx.TE_MULTILINE|wx.TE_READONLY)
		sizer.Add(tc, pos=(2, 0), span=(1, 5),
			flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=20)

		#next button
		goto_page6 = createBack(self, self.OnPage6)
		goto_page8 = createButton(self, self.OnPage8, "Install")

		#apply sizer to page
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(goto_page6, 0, wx.RIGHT, 20)
		hbox.Add(goto_page8)
		sizer.Add(hbox, pos=(3, 0), flag=wx.LEFT|wx.BOTTOM, border=20)

		#set sizer
		self.SetSizerAndFit(sizer)

	def OnPage8(self, event):
		self.data.writefiles()
		wx.PostEvent(self.parent, PageChangeEvent(page=finish))

	def OnPage6(self, event):
		wx.PostEvent(self.parent, PageChangeEvent(page=Page6))

def finish(parent, data):
	wx.GetApp().ExitMainLoop()


class Boss(wx.Frame):
	def __init__(self, parent, title):
		super(Boss, self).__init__(parent, title=title, size=(675, 520))
		self.data = stack.wizard.Data()
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

(PageChangeEvent, EVT_PAGE_CHANGE) = wx.lib.newevent.NewEvent()
(DialogChangeEvent, EVT_DIALOG_CHANGE) = wx.lib.newevent.NewEvent()

app = wx.App()
app.TopWindow = Boss(None, title='Stacki Installation')
app.TopWindow.Show()
app.MainLoop()
