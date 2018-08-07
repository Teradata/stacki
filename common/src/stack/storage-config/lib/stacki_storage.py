#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
#

import subprocess
import os
import sys


def attr2bool(s):
	if type(s) == type([]) and s:
		return 1

	if s and s.upper() in [ 'ALL', 'YES', 'Y', 'TRUE', '1' ]:
		return 1

	return 0


def sortDiskId(entry):
	try:
		key = entry['diskid']
		if not key:
			key = sys.maxint
	except:
		key = sys.maxint

	return key


# Called by outside scripts
def getDeviceList(disks):
	devices = []
	for disk in disks:
		for part in disk['part']:
			device = '/dev/%s' % part
			if device not in devices:
				devices.append(device)

		for raid in disk['raid']:
			device = '/dev/%s' % raid
			if device not in devices:
				devices.append(device)

		for lvm in disk['lvm']:
			device = '/dev/mapper/%s' % lvm
			if device not in devices:
				devices.append(device)
	return devices


# Called by outside scripts
def getHostDisks(nukedisks):
	#
	# create a dictionary for the attached currently configured 
	# storage. the format is:
	#
	#	disks = [{
	#		'device'	: 'sda',
	#		'diskid'	: 1,
	#		'part'		: [ 'sda1', 'sda2' ],
	#		'raid'		: [ 'md0', 'md1' ],
	#		'lvm'		: [ 'volgrp01-var', 'volgrp02-export' ],
	#		'nuke'		: 0
	#	}]
	#
	block_info = get_block_info()
	disks = []
	diskentry = None
	diskid = 1

	for name in block_info:
		mediatype = block_info[name]['devtype']
		# Skipping the header
		# Skip read-only and removable devices
		# Skip unkown device types
		if name.lower() == 'name' or \
				int(block_info[name]['removable']) or \
				int(block_info[name]['readonly']) or \
				mediatype not in [ 'disk', 'part', 'raid', 'lvm' ]:
			continue

		if mediatype.startswith('raid'):
			#
			# md mediatypes can be 'raid0', 'raid1', etc. let's
			# just shorten it to 'raid'.
			#
			mediatype = 'raid'

		if mediatype == 'disk':
			diskentry = None
			for disk in disks:
				if disk['device'] == name:
					diskentry = disk
					break

			if not diskentry:
				if nukedisks and (nukedisks[0] == '*' or name in nukedisks):
					nuke = 1
				else:
					nuke = 0

				disks.append({
					'device' : name,
					'diskid' : diskid,
					'part' : [],
					'raid' : [],
					'lvm' : [],
					'nuke' : nuke,
					# Need these to act like partitions for total disk size reporting in 'stack list host partition'
					'mountpoint' : '',
					'size' : int(int(block_info[name]['size']) / (1024 * 1024)),
					'start' : int(int(block_info[name]['start']) / (1024 * 1024)),
					'diskpart' : name,
					'fstype' : '',
					'uuid' : ''
				})

				for disk in disks:
					if disk['device'] == name:
						diskentry = disk
						break

				diskid = diskid + 1
		else:
			if name not in diskentry[mediatype]:
				diskentry[mediatype].append(name)

	if disks:
		disks.sort(key = sortDiskId)

	return disks


def getHostMountpoint(host_fstab, uuid, label):
	for part in host_fstab:
		if part['device'] == 'UUID=%s' % uuid:
			return part['mountpoint']
		elif part['device'] == 'LABEL=%s' % label:
			return part['mountpoint']

	return None


def getDiskPartNumber(disk):
	partnumber = 0

	p = subprocess.run([ 'blkid', '-o', 'export', '-s', 'PART_ENTRY_NUMBER', '-p', '/dev/%s' % disk ],
			   stdin=subprocess.PIPE,
			   stdout=subprocess.PIPE,
			   stderr=subprocess.PIPE)
	#
	# the above should only return one line
	#
	arr = p.stdout.decode().split('=')

	if len(arr) == 2:
		partnumber = arr[1].strip()

	return partnumber


# Called by outside scripts
def getHostPartitions(disks, host_fstab):
	partitions = []
	block_info = get_block_info()

	for d in disks:
		disk = d['device']

		p = subprocess.run([ 'lsblk', '-nrbo', 'NAME,MOUNTPOINT,FSTYPE', '/dev/%s' % disk ],
				   stdin=subprocess.PIPE, 
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)

		for l in p.stdout.decode().split('\n'):
			# Ignore empty lines
			if not l.strip():
				continue
			# Parse some of the data
			arr = l.split(' ')
			diskname = arr[0]
			mountpoint = arr[1]
			fstype = arr[2]

			# Ignore devices we don't have info for (live, zram, etc)
			if diskname not in block_info:
				continue
			# ignore the "whole" disk device (we are interested only in partitions)
			# Skipping the header or non-partitions:
			if diskname.lower() == 'name' or diskname == disk:
				continue

			try:
				size = int(int(block_info[diskname]['size']) / (1024 * 1024))
			except:
				size = 0

			if not mountpoint:
				mountpoint = getHostMountpoint(host_fstab, block_info[diskname]['uuid'], block_info[diskname]['label'])

			if mountpoint == '[SWAP]':
				mountpoint = 'swap'

			partnumber = getDiskPartNumber(diskname)

			disk_partitions = {}
			disk_partitions['device'] = disk
			disk_partitions['mountpoint'] = mountpoint
			disk_partitions['size'] = size
			disk_partitions['fstype'] = fstype
			disk_partitions['uuid'] = block_info[diskname]['uuid']
			disk_partitions['diskpart'] = diskname
			disk_partitions['start'] = int(int(block_info[diskname]['start']) / (1024 * 1024))

			if partnumber:
				disk_partitions['partnumber'] = partnumber

			if block_info[diskname]['label']:
				disk_partitions['options'] = '--label=%s' % block_info[diskname]['label']
			else:
				disk_partitions['options'] = ''

			partitions.append(disk_partitions)

	return partitions


# Called by outside scripts
def getHostFstab(devices):
	import tempfile

	host_fstab = []

	mountpoint = tempfile.mktemp()
	os.makedirs(mountpoint)
	fstab = mountpoint + '/etc/fstab'

	for device in devices:
		os.system('mount %s %s' % (device, mountpoint) + ' > /dev/null 2>&1')

		if os.path.exists(fstab):
			file = open(fstab)

			for line in file.readlines():
				entry = {}

				split_line = line.split()
				if len(split_line) < 3:
					continue

				if split_line[0][0] == '#':
					continue

				entry['device'] = split_line[0].strip()
				entry['mountpoint'] = split_line[1].strip()
				entry['fstype'] = split_line[2].strip()

				host_fstab.append(entry)

			file.close()

		os.system('umount %s 2> /dev/null' % mountpoint)

		if host_fstab:
			break

	try:
		os.removedirs(mountpoint)
	except:
		pass

	return host_fstab



def get_uuid_dict():
	"""
	Trying to avoid lsblk, but couldn't find a better way than following symlinks to get UUID.
	returns a dictionary where the keys are the '/dev/sda1' type device name and the value is the UUID:
		{'/dev/sda4': '5275ca28-e9f6-4dcc-97c1-4ea9f72f7ed4',
		'/dev/sda3': '4f013836-ce39-4cd5-8296-1d105f13ebf4',
		'/dev/sda2': 'e66453ff-4909-4b2b-97be-a233a0e238a4',
		'/dev/sda1': '07a03a78-dc74-439c-a0b9-2e44c90390e8'}
	"""
	uuid_dict = {}
	devpath = '/dev/disk/by-uuid/'
	for uuid in os.listdir(devpath):
		# cleanup the symlink path to absolute:
		uuid_dict[os.path.normpath(os.path.join(devpath, os.readlink(devpath + uuid)))] = uuid
	return uuid_dict


def get_label_dict():
	"""
	Trying to avoid lsblk, but couldn't find a better way than following symlinks to get labels.
	returns a dictionary where the keys are the '/dev/sda1' type device name and the value is the label:
	"""
	label_dict = {}
	devpath = '/dev/disk/by-label/'
	try:
		for label in os.listdir(devpath):
			# cleanup the symlink path to absolute:
			label_dict[os.path.normpath(os.path.join(devpath, os.readlink(devpath + label)))] = label
	except FileNotFoundError:
		pass
	return label_dict

def get_hidden_loops(holder, hidden=set()):
	for each_link in os.listdir(holder):
		symlink = os.readlink(os.path.join(holder + '/' + each_link))
		with open(os.path.normpath(os.path.join(holder + '/' + symlink)) + '/uevent') as uevent:
			for each_line in uevent.readlines():
				key, value = each_line.split('=')[:2]
				if key.lower() == 'devname':
					hidden.add(value.strip().lower())
	return hidden


def set_label_and_uuid(current_disk, uuid_dict, label_dict):
	"""
	This will try to set the uuid and label if possible.
	Otherwise it prints to stdout that it couldn't. It isn't necessarily an error, but is good to know.
	Crated these set_ functions because get_block_info was getting messy. Wanted to clean it up a little.
	"""
	current_disk['label'] = ''
	current_disk['uuid'] = ''
	try:
		current_disk['uuid'] = uuid_dict['/dev/' + current_disk['devname']]
	except KeyError as key_error:
		pass
	try:
		current_disk['label'] = label_dict['/dev/' + current_disk['devname']]
	except KeyError as key_error:
		pass
	return current_disk['uuid'], current_disk['label']


def set_size_and_start(current_disk, path ):
	"""
	Find the size of the disk and multiple it by the blocksize.
	If it is an partition also find where that partitions starts.
	Return each as an integer.
	"""
	current_disk['start'] = 0
	with open(path + "/size") as size:
		# I was nervous using a *512 in case we have 4k HDDs in the future, but
		# after looking into it, /sys/class/block/*/size is reported in *512 regardless of the true blocksize
		current_disk['size'] = int(size.readline().strip()) * 512
		if current_disk['devtype'] == 'partition':
			with open(path+ "/start") as start:
				current_disk['start'] = int(start.readline().strip()) * 512
	return current_disk['size'], current_disk['start']


def set_readonly_and_removable(current_disk, path):
	"""
	Determine if the device is readonly or removable
	Should return each as an int 0 or 1
	"""
	try:
		with open(path + "/removable") as removable:
			current_disk['removable'] = int(removable.readline().strip())
	# If the file doesn't exist, set to not removable.
	except FileNotFoundError:
		current_disk['removable'] = 0

	with open(path + "/ro") as ro:
		current_disk['readonly'] = int(ro.readline().strip())
	return current_disk['readonly'], current_disk['removable']


def get_block_info():
	"""
	Utilizing the sysfs instead of blockid commands so we don't have if statements for different OS version.
	 This returns more info than is needed, I would like to migrate more of the commands into this, but I need to
	 test lvm and raid type scenarios before committing to that.
	Example returned info:
		'sdb' : {'major': '8', 'minor': '16', 'devname': 'sdb', 'devtype': 'disk', 'size': 799535005696}
		'sda' : {'major': '8', 'minor': '0', 'devname': 'sda', 'devtype': 'disk', 'size': 799535005696}
		'sda1' : {'major': '8', 'minor': '1', 'devname': 'sda1', 'devtype': 'partition', 'size': 16778264576, 'start': '2048', 'uuid': '07a03a78-dc74-439c-a0b9-2e44c90390e8'}
		'sda2' :{'major': '8', 'minor': '2', 'devname': 'sda2', 'devtype': 'partition', 'size': 1052770304, 'start': '32772096', 'uuid': 'e66453ff-4909-4b2b-97be-a233a0e238a4'}
		'sda3' :{'major': '8', 'minor': '3', 'devname': 'sda3', 'devtype': 'partition', 'size': 16780361728, 'start': '34828288', 'uuid': '4f013836-ce39-4cd5-8296-1d105f13ebf4'}
		'sda4' :{'major': '8', 'minor': '4', 'devname': 'sda4', 'devtype': 'partition', 'size': 764921511936, 'start': '67602432', 'uuid': '5275ca28-e9f6-4dcc-97c1-4ea9f72f7ed4'}
	 """
	blocks = []
	class_block = '/sys/class/block/'

	# Grab these once, outside the loop.
	uuid_dict = get_uuid_dict()
	label_dict = get_label_dict()
	hidden_loops = set()

	for major_block_dev in os.listdir(class_block):
		current_disk = {}

		# Ignore loop devices, but first find their holders to ignore those as well
		if 'loop' in major_block_dev:
			hidden_loops = get_hidden_loops('/sys/block/' + major_block_dev + '/holders', hidden_loops)
			hidden_loops = get_hidden_loops(class_block + major_block_dev + '/holders', hidden_loops)
			continue

		# Read through uevent for some details on the block device and add them to our dictionary
		# eg: 'major' : 8, 'minor' : 0, 'devname' : sda, 'devtype' : disk
		with open(class_block + major_block_dev + '/uevent') as uevent:
			for each_line in uevent.readlines():
				key, value = each_line.split('=')[:2]
				key = key.strip().lower()
				value = value.strip().lower()
				current_disk[key] = value
		path = class_block + major_block_dev
		current_disk['size'], current_disk['start'] = set_size_and_start(current_disk, path)
		current_disk['readonly'], current_disk['removable'] = set_readonly_and_removable(current_disk, path)
		current_disk['uuid'], current_disk['label'] = set_label_and_uuid(current_disk, uuid_dict, label_dict)
		blocks.append(current_disk)

	# Now that we have all the info lets build a dictionary using the devname as the keys
	devname_dict = {}

	for each in blocks:
		if each['devname'] not in hidden_loops:
			devname_dict[each['devname']] = each
	return devname_dict
