#!/opt/stack/bin/python
import os
import sys

#try to get wxpython
try:
	import wx
except ImportError:
	HAS_WX = False
else:
	HAS_WX = True

import threading
import time
import subprocess
import stack.roll
import stack.pallet

class DownloadFrame(wx.Frame):
	"""This is a test frame for displaying progress of downloading pallets"""
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(600, 600), style=wx.STAY_ON_TOP)

		sizer = wx.GridBagSizer(5, 3)

		#logo
		png = wx.Image('/opt/stack/bin/logo.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		imageBitmap = \
			wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
		sizer.Add(imageBitmap, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=20)

		#text message
		self.lb = wx.StaticText(self, label='No downloads as of now...')

		#list of pallets
		panel = wx.Panel(self, -1)
		self.list1 = wx.ListCtrl(panel, size=(-1,200), style=wx.LC_REPORT)
		self.list1.InsertColumn(0, 'Status', width = 150)
		self.list1.InsertColumn(1, 'Pallet Name', width = 150)
		self.list1.InsertColumn(2, 'Version', width = 150)

		#init progress bar
		self.progress = wx.Gauge(self, range=100, size=(500,-1))
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.updatePulse)
		self.name = 'No pallet'
		self.version = ''
		self.count = 0

		#add elements to form
		sizer.Add(self.lb, pos=(1, 0), span=(1, 5), \
			flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=20)
		sizer.Add(self.progress, pos=(2, 0), span=(1, 5), \
			flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=20)
		sizer.Add(panel, pos=(3, 0), span=(1, 5), \
			flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=20)

		#finalize
		self.SetSizerAndFit(sizer)
		self.Show(True)

	def downloadNewPallet(self, name, ver, size=None):
		if size:
			self.size = size
		else:
			self.timer.Start(100) #milliseconds

		self.name = name
		self.version = ver
		self.lb.SetLabel("Downloading: " + self.name + " " + self.version);

	def completeNewPallet(self):
		self.list1.InsertStringItem(0, 'Downloaded')
		self.list1.SetStringItem(0, 1, self.name)
		self.list1.SetStringItem(0, 2, self.version)
		self.lb.SetLabel("Completed Downloading: " + self.name + " " + self.version);
		self.timer.Stop()

	def errorNewPallet(self, rc):
		self.list1.InsertStringItem(0, 'Error ' + str(rc))
		self.list1.SetStringItem(0, 1, self.name)
		self.list1.SetStringItem(0, 2, self.version)
		self.lb.SetLabel("Error in Downloading: " + self.name + " " + self.version);
		self.timer.Stop()

	def rebuildDistribution(self):
		self.lb.SetLabel("Now building distribution (this can take a while)...");

	def updatePallet(self, count):
		self.progress.SetValue(count)

	def pollDownload(self, name, ver):
		if name != self.name or ver != self.version:
			wx.CallAfter(self.downloadNewPallet, name, ver)

	def updatePulse(self, timer):
		self.progress.Pulse()

	def updateProgress(self, count):
		wx.CallAfter(self.updatePallet, count)

	def initPallet(self, name, ver, size=None):
		wx.CallAfter(self.downloadNewPallet, name, ver, size)

	def completePallet(self):
		wx.CallAfter(self.completeNewPallet)

	def errorPallet(self, rc):
		wx.CallAfter(self.errorNewPallet, rc)

	def doneMessage(self):
		time.sleep(2)
		wx.CallAfter(self.rebuildDistribution)

def do_download(dialog=None):

	#
	# make sure the DVD is mounted
	#
	cmd = 'mkdir -p /mnt/cdrom ; mount /dev/cdrom /mnt/cdrom'
	os.system(cmd)

	cmd = 'rm -f /install ; ln -s /mnt/sysimage/export/stack /install'
	os.system(cmd)

	g = stack.roll.Generator()
	getpallet = stack.pallet.GetPallet()

	filename = None
	if os.path.exists('/tmp/pallets.xml'):
		filename = '/tmp/pallets.xml'
	elif os.path.exists('/tmp/rolls.xml'):
		filename = '/tmp/rolls.xml'

	if not filename:
		if 0:
			#
			# XXX not sure if we need to do this
			#
			media = stack.media.Media()
			if media.mounted():
				media.ejectCD()

		sys.exit(0)

	g.parse(filename)
	pallets = g.rolls

	if dialog:
		getpallet.downloadDVDPallets(pallets, dialog)
		getpallet.downloadNetworkPallets(pallets, dialog)
	else:
		getpallet.downloadDVDPallets(pallets)
		getpallet.downloadNetworkPallets(pallets)

	if dialog:
		# display rebuild distribution message
		dialog.doneMessage()

	cmd = 'rm -f /install ; ln -s /mnt/sysimage/export/stack /install'
	os.system(cmd)

	if dialog:
		#close the dialog
		wx.CallAfter(dialog.Destroy)

	#eject DVD after completion
	media = stack.media.Media()
	if media.mounted():
		media.umountCD()
		media.ejectCD()

def start(func, *args): # helper method to run a function in another thread
	thread = threading.Thread(target=func, args=args)
	thread.setDaemon(True)
	thread.start()

def main():
	if noX or not HAS_WX:
		do_download()
	else:
		app = wx.App(False)
		dialog = DownloadFrame(None, "Downloading Pallets")
		start(do_download, dialog)
		app.MainLoop()

#begin
noX = False
if __name__ == '__main__':

	for s in sys.argv:
		if s == '--noX':
			noX = True
	main()
