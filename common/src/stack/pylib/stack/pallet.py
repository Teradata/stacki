# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import subprocess
import stack
import stack.media
import time


class GetPallet:
	def __init__(self):
		#
		# in a default installation, make sure /export points to a
		# partition *not* on the '/' partition
		#
		self.anaconda = None
		self.media = stack.media.Media()

		cwd = os.getcwd()
		os.chdir('/mnt/sysimage')
		try:
			os.symlink('state/partition1', 'export')
		except:
			pass
		os.chdir(cwd)

	def checkDVD(self, diskname):
		#
		# check that it is the right pallet CD
		#
		found_disk = 'false'
		while found_disk == 'false':
			diskid = self.media.getId()

			if diskname == diskid:
				found_disk = 'true'

			if found_disk == 'false':
				self.media.ejectCD()

				print('Put Pallet disk %s in drive' % diskname)
				# sleepless infinite polling makes sadness
				time.sleep(3)

	def downloadDVDPallets(self, pallets, dialog=None):
		#
		# function is used when progress dialog is available
		# poll the destination directory and get the latest created pallet info
		# update the progress bar with current block to total block ratio
		#
		def updateProgress():
			T = []
			P = {}
			basePalletDir = '/mnt/sysimage/export/stack/pallets'
			if os.path.exists(basePalletDir):

				folders = os.listdir(basePalletDir)
				if len(folders) > 0:
					# get last modified time of all folders in pallets directory
					for name in folders:
						palletDir = basePalletDir + "/" + name
						if os.path.isdir(palletDir):

							# get the disk size
							proc = subprocess.Popen(['du', 
										 '-b', 
										 palletDir,
										 '--summarize' ], 
										stdout=subprocess.PIPE, 
										stderr=subprocess.PIPE)
							(out, err) = proc.communicate()
							size = int(filter(None, out.split('\n'))[0].split('\t')[0])

							version = os.listdir(palletDir)[0]
							mtime = os.stat(palletDir)[8]
							T.append(mtime)
							P[mtime] = (name, version, size)

					if len(T) > 0:

						# take the latest created and write the filename
						# with current size as content
						T.sort()
						latest_time = T[-1]
						tup = P[latest_time]

						#
						# write filename and byte size
						#
						name = str(tup[0])
						version = str(tup[1])
						pallet = name + '---' + version

						# normalize the size
						size = tup[2]
						value = int((float(size) / self.totalsizes[pallet]) * 100)

						# if name and version is different
						if name != self.name or version != self.version:
							if self.name != '' and self.version != '':
								# update to a new pallet
								dialog.completePallet()
								dialog.initPallet(name, version, self.totalsizes[pallet])
								dialog.updateProgress(value)
							else:
								# start a new pallet
								dialog.initPallet(name, version, self.totalsizes[pallet])
								dialog.updateProgress(value)
						else:
							dialog.updateProgress(value)

						self.name = name
						self.version = version

		diskids = []
		for pallet in pallets:
			(name, version, release, arch, url, diskid) = pallet

			if diskid != '' and diskid not in diskids:
				diskids.append(diskid)

		diskids.sort()
		for d in diskids:
			if not dialog:
				#
				# ask the user to put the right media in the bay
				#
				self.checkDVD(d)

				#
				# for DVDs, we can't download individual pallets --
				# we get all of them off the DVD
				#
				basePalletDir = '/mnt/sysimage/export/stack/pallets'

				cmd = '/opt/stack/bin/stack add pallet '
				cmd += 'updatedb=n dir=%s' % basePalletDir
				os.system(cmd)

			if dialog:
				#
				# ask the user to put the right media in the bay
				#
				self.checkDVD(d)

				# dict total sizes of DVD pallets
				self.totalsizes = {}

				# on the DVD look for roll-*.xml and put path into a list
				proc = subprocess.Popen(['find', 
							 '/mnt/cdrom/', 
							 '-type', 'f', 
							 '-name', 'roll-*.xml'], 
							stdout=subprocess.PIPE, 
							stderr=subprocess.PIPE)
				(out, err) = proc.communicate()
				P = filter(None, out.split('\n'))

				# get name and version of each pallet from list and store the sizes for each
				for path in P:
					info = path.split('/')

					if len(info) < 5:
						continue

					name = info[3]
					version = info[4]
					release = info[5]

					pallet = name + '---' + version
					palletPath = '/mnt/cdrom/' + name + '/' + version + '/' + release + '/'

					# get the size of pallet
					proc = subprocess.Popen(['du', '-b', palletPath, 
								 '--summarize'], 
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
					(out, err) = proc.communicate()

					size = int(filter(None, out.split('\n'))[0].split('\t')[0])
					self.totalsizes[pallet] = size

				#
				# for DVDs, we can't download individual pallets --
				# we get all of them off the DVD
				#
				basePalletDir = '/mnt/sysimage/export/stack/pallets'

				# init the name and version tracking variables for updateProgress()
				self.name = ''
				self.version = ''

				# totalsize is only used as a flag now
				dialog.initPallet(self.name, self.version, 100)

				# start download DVD pallets
				arg = 'dir=' + basePalletDir
				proc = subprocess.Popen(['/opt/stack/bin/stack', 
							 'add', 'pallet', 'updatedb=n', arg ], 
							stdout=subprocess.PIPE, 
							stderr=subprocess.PIPE)

				# while DVD pallets download, update progress bar
				while proc.poll() is None:
					time.sleep(0.2)
					updateProgress()

				# when done, force a complete
				dialog.updateProgress(100)
				dialog.completePallet()

			if self.media.mounted():
				self.media.ejectCD()

	def downloadNetworkPallets(self, pallets, dialog=None):
		for pallet in pallets:
			(name, version, release, arch, url, diskid) = pallet

			if diskid != '':
				continue

			path = os.path.join(name, version, release, 'redhat', arch)
			purl = os.path.join(url, path)
			cutdirs = len(purl.split(os.sep)) - 3
			localpath = os.path.join(
				'/mnt/sysimage/export/stack/pallets/', path)

			os.system('mkdir -p %s' % localpath)
			os.chdir(localpath)

			flags = '-m -np -nH --dns-timeout=3 '
			flags += '--connect-timeout=3 '
			flags += '--read-timeout=10 --tries=3'

			cmd = '/usr/bin/wget %s --cut-dirs=%d %s' % (flags,
				cutdirs, purl)

			if not dialog:
				os.system(cmd)

			if dialog:
				# spider mode command
				spi = cmd.split()
				spi.append('--spider')

				proc = subprocess.Popen(spi,
							stdout=subprocess.PIPE, 
							stderr=subprocess.PIPE)
				(out, err) = proc.communicate()

				totalsize = 0
				err = err.replace('\n', ' ')

				# get total size in KB
				A = filter(None, err.split("Length:"))
				for i in A:
					if '[application' in i:
						try:
							filesize = int(i.split()[0])
						except:
							filesize = 1

						totalsize += int(round(filesize * 0.001))

				# totalsize is only used as a flag now
				dialog.initPallet(name, version, totalsize)

				cmd = cmd.split()
				proc = subprocess.Popen(cmd,
							stdout=subprocess.PIPE, 
							stderr=subprocess.PIPE)

				# update the progress bar
				size = 0
				while proc.poll() is None:
					l = proc.stderr.readline()
					if len(l.split()) == 9:
						size += 50
						value = int((float(size) / totalsize) * 100)
						if value <= 100:
							dialog.updateProgress(value)

				dialog.updateProgress(100)
				dialog.completePallet()

			#
			# if this is the stacki pallet for redhat7 then we need to
			# copy the LiveOS and images directories into the 
			# destination
			#
			if name == 'stacki' and stack.release == 'redhat7':
				os.chdir(localpath)

				purl = os.path.join(url, 'LiveOS')
				cutdirs = len(purl.split(os.sep)) - 4

				cmd = '/usr/bin/wget %s --cut-dirs=%d %s' \
					% (flags, cutdirs, purl)
				os.system(cmd)

				purl = os.path.join(url, 'images')
				cutdirs = len(purl.split(os.sep)) - 4

				cmd = '/usr/bin/wget %s --cut-dirs=%d %s' \
					% (flags, cutdirs, purl)
				os.system(cmd)
