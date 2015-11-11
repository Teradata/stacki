#!/opt/stack/bin/python

import subprocess
import shlex
import syslog
import string
import os
import re
import tempfile
import sys
sys.path.append('/usr/lib/anaconda')

import time

class StackPartition:
	saved_fstab = []
	raidinfo = ''
	mountpoints = []

	def getDisks(self):
		if not os.path.exists('/tmp/discovered.disks'):
			subprocess.call(['/opt/stack/lib/discover_disks.py'])

		disks = []
		file = open('/tmp/discovered.disks', 'r')
		for line in file.readlines():
			l = string.split(line)
			if len(l) > 0 and l[0] == 'disks:':
				for d in l[1:]:
					disks.append(d)

		file.close()

		return disks

	def getRaids(self):
		raids = []

		if os.path.exists('/dev/md/md-device-map'):
			file = open('/dev/md/md-device-map', 'r')
			for line in file.readlines():
				l = string.split(line)
				if len(l) > 0 and l[0][0:2] == 'md':
					raids.append(l[0])
			file.close()

		return raids

	def gptDrive(self, devname):
		#
		# if this is a drive with a GPT format, then return '1'
		#
		retval = 0

		cmd = '%s /dev/%s print -s 2> /dev/null' % \
			(self.parted, devname)

		label = 'Disk label type:'
		for line in os.popen(cmd).readlines():
			if len(line) > len(label) and \
				line[0:len(label)] == label:

				l = string.split(line)
				if len(l) > 3 and l[3] == 'gpt':
					retval = 1
					break

		return retval


	def getDevice(self, str):
		device = ''

		a = string.split(str, '/dev/')
		if len(a) > 1:
			device = a[1]

		return string.strip(device)


	def getSectorStart(self, str):
		sectorstart = ''

		a = string.split(str, '=')
		if len(a) > 1 and string.strip(a[0]) == 'start':
			sectorstart = a[1]
		else:
			sectorstart = a[0]

		return string.strip(sectorstart)


	def getPartitionSize(self, str):
		partitionsize = ''

		a = string.split(str, '=')
		if len(a) > 1 and string.strip(a[0]) == 'size':
			partitionsize = a[1]
		else:
			partitionsize = a[0]

		return string.strip(partitionsize)


	def getPartId(self, str):
		partid = ''

		a = string.split(str, '=')
		if len(a) > 1 and string.strip(a[0]) == 'Id':
			partid = a[1]
		else:
			partid = a[0]
		
		return string.strip(partid)


	def getFsType(self, mntpoint):
		return self.findFsTypeInFstab(mntpoint)


	def getBootFlags(self, str):
		return string.strip(str)
		

	def getMountPoint(self, devicename):
		mntpoint = ''
		uuid	= ''

		cmd = 'blkid -o value -s UUID /dev/%s' % devicename
		cmd += ' 2> /dev/null'
		uuid = os.popen(cmd).readline().strip()
		if len(uuid) > 0:
			mntpoint = self.findMntInFstab("UUID=%s" % uuid)
		
		if mntpoint == '':
			mntpoint = self.findMntInFstab('/dev/' + devicename)

		if mntpoint == '':
			#
			# see if the device is part of a raidset
			#
			mntpoint = self.getRaidName(devicename)

		if mntpoint == '':
			cmd = '%s /dev/%s 2> /dev/null' % \
				(self.e2label, devicename)
			label = os.popen(cmd).readlines()

			label = string.join(label)
			id = 'LABEL=%s' % (label[:-1])

			mntpoint = self.findMntInFstab(id)

		return (mntpoint,uuid)


	def getRaidName(self, partition_device):
		raidname = ''

		for info in self.raidinfo:
			if len(info) > 3:
				(device, partitions, raidlevel,
					num_partitions) = info

				if partition_device in partitions:
					raidname = 'raid.%s' % partition_device
					break

		return raidname


	def findMntInFstab(self, identifier):
		for line in self.saved_fstab:
			l = string.split(line)
			if len(l) > 0:
				if l[0] == identifier:
					return l[1]

		return ''


	def findFsTypeInFstab(self, mntpoint):
		for line in self.saved_fstab:
			l = string.split(line)
			if len(l) > 2:
				if l[1] == mntpoint:
					return l[2]

		return ''


	def formatPartedNodePartInfo(self, devname, parts):
		#
		# this function parses partition info from 'parted'
		#
		partinfo = []
		
		for number in parts.keys():
			part = parts[number]

			if devname[0:2] == 'md':
				device = devname
			elif len(devname) > 4 and devname[0:5] == 'cciss':
				#
				# special case for HP smart array
				# controllers
				#
				device = devname + 'p' + '%s' % number
			else:
				device = devname + '%s' % number

			#
			# placeholder -- currently not getting the partition
			# id
			#
			partid = ''

			if 'linux-swap' in part['fs']:
				mntpoint = 'swap'
				uuid = ''
			else:
				mntpoint,uuid = self.getMountPoint(device)

			partinfo.append('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (device,
				part['start'], part['size'], partid,
				part['fs'], part['flags'], '', mntpoint, uuid))

		# print 'formatPartedNodePartInfo:partinfo: ', partinfo

		return partinfo


	def parsePartInfo(self, info):
		n = string.split(info, ',')

		if len(n) != 9:
			return ('', '', '', '', '', '', '', '','')

		device = string.strip(n[0])
		sectorstart = string.strip(n[1])
		partitionsize = string.strip(n[2])
		partid = string.strip(n[3])
		fstype = string.strip(n[4])
		bootflags = string.strip(n[5])
		partflags = string.strip(n[6])
		mntpoint = string.strip(n[7])
		uuid	= string.strip(n[8])

		return (device, sectorstart, partitionsize, partid, 
			fstype, bootflags, partflags, mntpoint, uuid)


	def getDiskInfo(self, disk):
		syslog.syslog('getDiskInfo: disk:%s' % (disk))

		cmd = '%s /dev/%s print -m -s' % (self.parted, disk)
		p = subprocess.Popen(shlex.split(cmd), stdin = None,
			stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		p.wait()
		o, e = p.communicate()

		partinfo = []
		for line in o.split(';\n'):
			if line:
				partinfo.append(line)

		#
		# ignore the first line. the first line describes the 'units'
		# that the disk info will be in, e.g., 'BYT;' means 'bytes'.
		#
		# and if there are less than 2 lines, then this disk has no
		# info
		#
		diskinfo = {}
		diskinfo[disk] = {'size': 0, 'label': None, 'parts': {}}

		if len(partinfo) < 2:
			return diskinfo

		#
		# the second line describes the whole disk's parameters
		#
		diskparams = partinfo[1].split(':')
		diskinfo[disk]['size'] = diskparams[1]
		diskinfo[disk]['label'] = diskparams[5]

		parts = {}

		#
		# the remaining entries describe the disk's partitions
		#
		for p in partinfo[2:]:
			part = p.split(':')

			if len(part) != 7:
				continue

			try:
				number = int(part[0])
			except:
				continue

			parts[number] = { 'start': part[1], 'end': part[2],
				'size': part[3], 'fs': part[4],
				'name': part[5], 'flags': part[6]}

		diskinfo[disk]['parts'] = parts
		syslog.syslog('getDiskInfo: parts:%s' % (diskinfo))

		return diskinfo


	def getRaidLevel(self, device):
		level = None

		cmd = '%s --query --detail ' % (self.mdadm)
		cmd += '/dev/%s' % (device)
		for line in os.popen(cmd).readlines():
			l = line.split()
			if len(l) > 3 and l[0] == 'Raid' and l[1] == 'Level':
				if l[3][0:4] == 'raid':
					level = l[3][4:]
					break
		
		return level


	def getRaidParts(self, device):
		parts = []

		foundparts = 0
		cmd = '%s --query --detail ' % (self.mdadm)
		cmd += '/dev/%s' % (device)
		for line in os.popen(cmd).readlines():
			l = line.split()
			if len(l) > 4 and l[3] == 'RaidDevice':
				foundparts = 1
				continue

			if foundparts == 0:
				continue

			if len(l) == 0:
				continue
			
			part = l[-1].split('/')
			parts.append('raid.%s' % part[-1])

		return ' '.join(parts)

	def getNodePartInfo(self, disks):
		arch = os.uname()[4]

		partinfo = []
		nodedisks = {}

		# print 'getNodePartInfo:disks ', disks

		#
		# try to get the 
		#
		for line in self.getFstab(disks):
			self.saved_fstab.append(line)

		for devname in disks:
			diskinfo = self.getDiskInfo(devname)

			#
			# add an entry for the disk device itself,
			# (e.g., 'sda', 'sdb', etc.)
			#
			if devname[0:2] != 'md':
				partinfo.append("%s,,%s,,,,,," % (devname,
					diskinfo[devname]['size']))

			if 'parts' in diskinfo[devname]:
				partinfo += self.formatPartedNodePartInfo(
					devname, diskinfo[devname]['parts'])

		syslog.syslog('getNodePartInfo: partinfo:%s' % (partinfo))

		for node in partinfo:
			n = self.parsePartInfo(node)

			(nodedevice, nodesectorstart, nodepartitionsize,
				nodepartid, nodefstype, nodebootflags,
				nodepartflags, nodemntpoint, nodeuuid) = n

			if (len(nodedevice) > 2) and (nodedevice[0:2] == 'md'):
				nodepartflags = '--level=%s' % \
					self.getRaidLevel(nodedevice)

				nodebootflags = self.getRaidParts(nodedevice)

				n = (nodedevice, nodesectorstart,
					nodepartitionsize,
					nodepartid, nodefstype,
					nodebootflags,
					nodepartflags, nodemntpoint, nodeuuid)

			elif nodebootflags != '':
				if 'raid' in nodebootflags.split():
					nodemntpoint = 'raid.%s' % (nodedevice)

					n = (nodedevice, nodesectorstart,
						nodepartitionsize,
						nodepartid, nodefstype,
						nodebootflags,
						nodepartflags, nodemntpoint, nodeuuid)
				
			if nodedevice != '':
				key = ''
				for disk in disks:
					if len(disk) <= len(nodedevice) and \
						disk == nodedevice[0:len(disk)]:

						key = disk
						break

				if key != '':
					if key not in nodedisks:
						nodedisks[key] = [n]
					else:
						nodedisks[key].append(n)

		syslog.syslog('getNodePartInfo:nodedisks:%s' % (nodedisks))

		return nodedisks


	def listDiskPartitions(self, disk):
		if disk[0:2] == 'md':
			return [ (disk, 'dummy') ]

		diskinfo = self.getDiskInfo(disk)
		if 'parts' not in diskinfo[disk]:
			return []

		if len(disk) > 4 and disk[0:5] == 'cciss':
			#
			# special case for HP smart array
			# controllers
			#
			diskname = disk + 'p'
		else:
			diskname = disk

		list = []
		# print 'diskinfo: (%s)' % diskinfo
		for number in diskinfo[disk]['parts'].keys():
			part = diskinfo[disk]['parts'][number]
			list.append(('%s%d' % (diskname, number), part['fs']))

		return list


	def defaultDataDisk(self, disk):
		basename = '/state/partition'
		parts = []

		i = 1
		while 1:
			nextname = '%s%d' % (basename, i)
			if nextname not in self.mountpoints:
				break
			i = i + 1

		p = 'part '
		p += '%s --size=1 ' % (nextname)
		p += '--fstype=ext4 --grow --ondisk=%s ' % (disk)
		self.mountpoints.append(nextname)
		parts.append(p)

		return parts


	def StackGetPartsize(self, mountpoint):
		size = 0

		if mountpoint == 'root':
			size = 16000
		elif mountpoint == 'var':
			size = 4000
		elif mountpoint == 'swap':
			size = 1000

		return size


	def defaultRootDisk(self, disk):
		arch = os.uname()[4]
		parts = []

		if arch == 'ia64':
			p = 'part /boot/efi --size=1000 --fstype=vfat '
			p += '--ondisk=%s\n' % (disk)

		p = 'part '
		p += '/ --size=%d ' % (self.StackGetPartsize('root'))
		p += '--fstype=ext4 --ondisk=%s ' % (disk)
		self.mountpoints.append('/')
		parts.append(p)

		p = 'part '
		p += '/var --size=%d ' % (self.StackGetPartsize('var'))
		p += '--fstype=ext4 --ondisk=%s ' % (disk)
		self.mountpoints.append('/var')
		parts.append(p)

		p = 'part '
		p += 'swap --size=%d ' % (self.StackGetPartsize('swap'))
		p += '--fstype=swap --ondisk=%s ' % (disk)
		self.mountpoints.append('swap')
		parts.append(p)

		#
		# greedy partitioning
		#
		parts += self.defaultDataDisk(disk)

		return parts


	def getFstab(self, disks):
		if os.path.exists('/upgrade/etc/fstab'):
			file = open('/upgrade/etc/fstab')
			lines = file.readlines()
			file.close()
			return lines

		#
		# if we are here, let's go look at all the disks for /etc/fstab
		#
		mountpoint = tempfile.mktemp()
		os.makedirs(mountpoint)
		fstab = mountpoint + '/etc/fstab'

		lines = []
		for disk in disks:
			for (partition, fstype) in \
					self.listDiskPartitions(disk):

				if not fstype or 'linux-swap' in fstype:
					continue

				os.system('mount /dev/%s %s' \
					% (partition, mountpoint) + \
					' > /dev/null 2>&1')

				if os.path.exists(fstab):
					file = open(fstab)
					lines = file.readlines()
					file.close()

				os.system('umount %s 2> /dev/null' %
					(mountpoint))

				if len(lines) > 0:
					try:
						os.removedirs(mountpoint)
					except:
						pass
					return lines

		#
		# if we are here, let's see if there are any LVMs and try
		# to mount them
		#
		cmd = 'lvdisplay -C --noheadings'
		p = subprocess.Popen(shlex.split(cmd), stdin = None,
			stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		p.wait()
		o, e = p.communicate()

		volgroups = []
		for line in o.split('\n'):
			if not line:
				continue

			lv = None
			vg = None
			l = line.split()
			if len(l) > 1:
				lv = l[0].strip()
				vg = l[1].strip()

			if not lv or not vg:
				continue

			syslog.syslog('getFstab: lv:%s' % (lv))
			syslog.syslog('getFstab: vg:%s' % (vg))

			if vg not in volgroups:
				volgroups.append(vg)

				#
				# start this volume group
				#
				syslog.syslog('getFstab:starting VG %s' % vg)
				os.system('vgchange %s -a y' % vg + \
					' > /dev/null 2>&1')

			os.system('mount /dev/%s/%s %s' \
					% (vg, lv, mountpoint) + \
					' > /dev/null 2>&1')

			if os.path.exists(fstab):
				file = open(fstab)
				lines = file.readlines()
				file.close()

			os.system('umount %s 2> /dev/null' %
				(mountpoint))

			if len(lines) > 0:
				break

		try:
			os.removedirs(mountpoint)
		except:
			pass

		return lines


	def isStackDisk(self, partinfo, touchit = 0):
		retval = 0

		mountpoint = tempfile.mktemp()
		os.makedirs(mountpoint)

		for part in partinfo:
			(dev,start,size,id,fstype,bootflags,partflags,mnt,uuid) = \
				part

			if not fstype or 'linux-swap' in fstype:
				continue

			devname = '/dev/%s' % (dev)

			os.system('mount %s %s' % (devname, mountpoint))

			try:
				filename = mountpoint + '/.stack-release'

				if touchit == 1:
					os.system('touch %s' % filename)

				if os.path.exists(filename):
					retval = 1
			except:
				pass

			os.system('umount %s' % (mountpoint) +
				' > /dev/null 2>&1')

			if retval == 1:
				break

		try:
			os.removedirs(mountpoint)
		except:
			pass

		return retval


	def addPartitions(self, nodepartinfo, format):
		arch = os.uname()[4]
		parts = []

		#
		# for each partition on a drive, build a partition
		# specification for anaconda
		#
		for node in nodepartinfo:
			if len(node) == 1:
				continue

			(nodedevice, nodesectorstart, nodepartitionsize,
				nodepartid, nodefstype, nodebootflags,
				nodepartflags, nodemntpoint, nodeuuid) = node

			if nodemntpoint == '' or nodemntpoint[0:4] == 'raid':
				continue

			#
			# only add raid partitions if they have a mountpoint
			# defined by their respective 'md' device.
			#
			# anaconda will crash if there is not a valid
			# mountpoint for the md device
			#
			if nodepartid == 'fd':
				if not self.getRaidMountPoint(nodedevice):
					continue

			args = [ nodemntpoint ]

			if (nodemntpoint != '/' and nodemntpoint != '/var' \
				and nodemntpoint != '/boot') and not format:
				args.append('--noformat')
			else:
				if nodefstype == '':
					args += [ '--fstype', self.fstype ]
				else:
					args += [ '--fstype', nodefstype ]

			israid = 0

			if len(nodedevice) > 2 and nodedevice[0:2] == 'md':
				israid = 1

				args += [ "--device=%s" % (nodedevice) ]

				if nodepartflags != '':
					args += [ nodepartflags ]

				args += [ '--useexisting' ]
			else:
				args += [ "--onpart", nodedevice ]

			if israid:
				parts.append('raid %s' % (string.join(args)))
			else:
				parts.append('part %s' % (string.join(args)))

			self.mountpoints.append(nodemntpoint)

		return parts


	def compareDiskInfo(self, dbpartinfo, nodepartinfo):
		if len(dbpartinfo) != len(nodepartinfo):
			return 0

		for db in dbpartinfo:
			if len(db) == 1:
				continue
                
			(dbdevice, dbsectorstart, dbpartsize, dbpartid,
				dbfstype, dbbootflags, dbpartflags,
				dbmntpoint) = db
                
			found = 0
			for node in nodepartinfo:
				if len(node) == 1:
					continue
                        
				(nodedevice, nodesectorstart, nodepartsize,
					nodepartid, nodefstype, nodebootflags,
					nodepartflags, nodemntpoint, nodeuuid) = node
                        
				# print 'compareDiskInfo:node: ', node
				# print 'compareDiskInfo:db: ', db

				if dbsectorstart == nodesectorstart and \
					dbpartsize == nodepartsize and \
					dbpartid == nodepartid and \
					dbfstype == nodefstype and \
					dbbootflags == nodebootflags and \
					dbpartflags == nodepartflags and \
					dbmntpoint == nodemntpoint:

					found = 1
					break
                        
			if not found:
				return 0
                        
		return 1


	def __init__(self):
		#
		# setup logging
		#
		syslog.openlog('STACKI', syslog.LOG_DEBUG, syslog.LOG_LOCAL0)

		#
		# setup path to commands
		#
		if os.path.exists('/mnt/runtime/usr/sbin/parted'):
			self.parted = '/mnt/runtime/usr/sbin/parted'
		else:
			self.parted = '/sbin/parted'

		if os.path.exists('/mnt/runtime/usr/sbin/e2label'):
			self.e2label = '/mnt/runtime/usr/sbin/e2label'
		else:
			self.e2label = '/sbin/e2label'

		if os.path.exists('/mnt/runtime/usr/sbin/mdadm'):
			self.mdadm = '/mnt/runtime/usr/sbin/mdadm'
		else:
			self.mdadm = '/sbin/mdadm'

		return

