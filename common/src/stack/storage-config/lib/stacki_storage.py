#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
#

import subprocess
import os

from stack_site import attributes

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
			key = sys.maxsize
	except:
		key = sys.maxsize

	return key


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
	lsblk = ['lsblk', '--noheadings', '-lio', 'NAME,RM,RO,TYPE']
	# sles 11 doesn't support the TYPE column
	if attributes.get('os.version') == "11.x" and attributes.get('os') == "sles":
		lsblk = ['lsblk', '--noheadings', '-lio', 'NAME,RM,RO']
	p = subprocess.run(lsblk,
			   stdin=subprocess.PIPE,
			   stdout=subprocess.PIPE,
			   stderr=subprocess.PIPE)
	disks = []
	diskentry = None
	diskid = 1

	for l in p.stdout.decode().split('\n'):
		# Ignore empty lines
		if not l.strip():
			continue

		#
		# Skip read-only and removable devices
		#
		arr = l.split()
		name = arr[0].strip()
		removable = arr[1].strip()
		readonly = arr[2].strip()
		if attributes.get('os.version') == "11.x" and attributes.get('os') == "sles":
			mediatype = get_sles11_media_type(name)
		else:
			mediatype = arr[3].strip()

		if mediatype.startswith('raid'):
			#
			# md mediatypes can be 'raid0', 'raid1', etc. let's
			# just shorten it to 'raid'.
			#
			mediatype = 'raid'

		if removable == '1' or readonly == '1' or mediatype not in [ 'disk', 'part', 'raid', 'lvm' ]:
			continue

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
					'device'	: name,
					'diskid'	: diskid,
					'part'		: [],
					'raid'		: [],
					'lvm'		: [],
					'nuke'		: nuke 
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


def getHostPartitions(disks, host_fstab):
	partitions = []

	for d in disks:
		disk = d['device']
	
		p = subprocess.run([ 'lsblk', '-nrbo', 'NAME,SIZE,UUID,LABEL,MOUNTPOINT,FSTYPE', '/dev/%s' % disk ],
				   stdin=subprocess.PIPE, 
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)

		for l in p.stdout.decode().split('\n'):
			# Ignore empty lines
			if not l.strip():
				continue

			arr = l.split(' ')

			#
			# ignore the "whole" disk device (we are interested
			# only in partitions)
			#
			diskname = arr[0]
			if diskname == disk:
				continue

			try:
				size = int(int(arr[1]) / (1024 * 1024))
			except:
				size = 0

			uuid = arr[2]
			label = arr[3]
			mountpoint = arr[4]
			fstype = arr[5]

			if not mountpoint:
				mountpoint = getHostMountpoint(host_fstab,
					uuid, label)

			if mountpoint == '[SWAP]':
				mountpoint = 'swap'

			partnumber = getDiskPartNumber(diskname)

			disk_partitions = {}
			disk_partitions['device'] = disk
			disk_partitions['mountpoint'] = mountpoint
			disk_partitions['size'] = size
			disk_partitions['fstype'] = fstype
			disk_partitions['uuid'] = uuid
			disk_partitions['diskpart'] = diskname

			if partnumber:
				disk_partitions['partnumber'] = partnumber

			if label:
				disk_partitions['options'] = \
					'--label=%s' % label
			else:
				disk_partitions['options'] = ''

			partitions.append(disk_partitions)

	return partitions


def getHostFstab(devices):
	import tempfile

	host_fstab = []

	mountpoint = tempfile.mktemp()
	os.makedirs(mountpoint)
	fstab = mountpoint + '/etc/fstab'

	for device in devices:
		os.system('mount %s %s' % (device, mountpoint) + \
			' > /dev/null 2>&1')

		if os.path.exists(fstab):
			file = open(fstab)

			for line in file.readlines():
				entry = {}

				l = line.split()
				if len(l) < 3:
					continue

				if l[0][0] == '#':
					continue

				entry['device'] = l[0].strip()
				entry['mountpoint'] = l[1].strip()
				entry['fstype'] = l[2].strip()

				host_fstab.append(entry)

			file.close()

		os.system('umount %s 2> /dev/null' % (mountpoint))

		if host_fstab:
			break

	try:
		os.removedirs(mountpoint)
	except:
		pass

	return host_fstab


def get_sles11_media_type(dev_name):
	"""Determines disk and partition for SLES 11.
	Because SLES 11 doesn't support TYPE field on lsblk commands

	`dev_name` is expected to be just the block device, without leading /dev/
	return value should only ever be 'loop', 'part', or 'disk'
	"""
	p = subprocess.run(f"hwinfo --block --short --only /dev/{dev_name}",
		shell=True,
		encoding='utf-8',
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	# hwinfo --only against a block device will return either empty string OR something like:
	# partition:
	#   /dev/sda1		Partition
	# OR
	# disk:
	#   /dev/sda		Some crazy string
	# 'Some crazy string' is maybe controller model, or the iscsi target type, or maybe just 'disk'
	# anyway, just steal line 0 for the type
	# other possible line 0 values can be 'cdrom', 'unknown', depending on the state of system

	# If we can't find what we are looking for, lie and say its "loop"
	blk_type = 'loop'
	if p.stdout == '':
		return blk_type

	# we could probably do without a loop here, but I don't fully trust the output of hwinfo
	for l in p.stdout.splitlines():
		# there should be just two lines...
		arr = l.strip().split()

		# line 0
		if len(arr) == 1 and arr[0] == 'partition:':
			blk_type = 'part'
			continue

		# line 0
		if len(arr) == 1 and arr[0] == 'disk:':
			blk_type = 'disk'
			continue

		# line 1
		if f'/dev/{dev_name}' == arr[0]:
			return blk_type

