#!/opt/stack/bin/python

from __future__ import print_function
import sys
import string
import stack_partition
import os
import subprocess
import shlex


def initializeDisk(disk):
	cmd = '/sbin/mdadm --stop --scan > /dev/null 2>&1'
	os.system(cmd)

	cmd = '/usr/sbin/parted -s /dev/%s' % disk
	cmd += ' mklabel gpt > /dev/null 2>&1'
	os.system(cmd)


def breakdownArgs(line):
	breakdown = []
	for x in line.split():
		breakdown += x.split('=')

	return breakdown


def getDisk(partline):
	part = breakdownArgs(partline)
	i = 0
	for p in part:
		if p == '--ondisk' and len(part) > i + 1:
			return part[i + 1]
		i += 1

	return None


def findBootDisk(disks):
	disk = None

	if os.path.exists('/tmp/user_partition_info'):
		file = open('/tmp/user_partition_info', 'r')
		for line in file.readlines():
			part = breakdownArgs(line)
			if len(part) > 1 and part[1] == '/':
				disk = getDisk(line)
		file.close()

	if not disk:
		disk = disks[0]

	return disk


def frontend(nodestorage, disks, raids):
	parts = []

	#	
	# for a frontend, it is either: 1) manual, or 2) default boot disk.
	# if we made it here, then we are at #2, so we need to wipe the boot
	# disk
	#
	disk = findBootDisk(disks)
	if disk:
		initializeDisk(disk)

	if os.path.exists('/tmp/user_partition_info'):
		file = open('/tmp/user_partition_info', 'r')
		for line in file.readlines():
			parts.append(line[:-1])
		file.close()

	return parts


def backend(nodestorage, disks, raids):
	parts = []

	#
	# get partition info for all the disks
	#
	disks = disks + raids
	nodedisks = nodestorage.getNodePartInfo(disks)

	#
	# save nodedisks in a temporary variable. if we have a match
	# in the loop below, we can delete an entry from 'i' and not
	# corrupt nodedisks while will loop over nodedisks's entries
	#
	i = nodedisks

	#
	# reconnect all Stack disks
	#
	for disk in nodedisks.keys():
		if nodestorage.isStackDisk(nodedisks[disk]):
			part = nodestorage.addPartitions(nodedisks[disk],
				format = 0)
			parts += part

			#
			# this disk is recognized, so remove it from
			# nodedisks and disks
			#
			del i[disk]
			disks.remove(disk)
			
	nodedisks = i

	#
	# reconnect all disks that match in the database
	#
	dbpartinfo = {}
	if os.path.exists('/tmp/db_partition_info.py'):
		sys.path.append('/tmp')
		import db_partition_info

		dbpartinfo = db_partition_info.dbpartinfo

	for disk in nodedisks.keys():
		if dbpartinfo.has_key(disk) and \
			nodestorage.compareDiskInfo(dbpartinfo[disk],
				nodedisks[disk]):

			part = nodestorage.addPartitions(nodedisks[disk],
				format = 0)
			parts += part

			#
			# this disk is recognized, so remove it from
			# nodedisks and disks
			#
			del i[disk]
			disks.remove(disk)

	if os.path.exists('/tmp/user_partition_info') and len(parts) == 0:
		#
		# only do user partitioning if we *didn't* reconnect *any*
		# of the disks
		#
		initdisks = []

		file = open('/tmp/user_partition_info', 'r')
		for line in file.readlines():
			parts.append(line[:-1])

			#
			# if we are in this section, then we are discovering
			# this disk for the first time, so we need to
			# initialize the disk.
			#
			disk = getDisk(line[:-1])
			if disk and disk not in initdisks:
				initdisks.append(disk)
			
		file.close()

		for disk in initdisks:
			initializeDisk(disk)

	return parts


def lvm(nodestorage):
	cmd = 'lvdisplay -C --noheadings'
	p = subprocess.Popen(shlex.split(cmd), stdin = None,
		stdout = subprocess.PIPE, stderr = subprocess.PIPE)

	p.wait()
	o, e = p.communicate()

	lvms = []
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
	
		# print 'lv: ', lv
		# print 'vg: ', vg

		mnt = nodestorage.findMntInFstab('/dev/mapper/%s-%s' % (vg, lv))
		flags = '--noformat' 

		if mnt in [ '/', '/var' ]:
			flags = '--useexisting'

		lvms.append('logvol %s --name=%s --vgname=%s %s' %
			(mnt, lv, vg, flags))

	return lvms


##
## main
##
if not os.path.exists('/tmp/user_partition_info') and \
		os.path.exists('/tmp/system_partition_info'):
	os.rename('/tmp/system_partition_info',
		'/tmp/user_partition_info')

partscheme = None
if os.path.exists('/tmp/user_partition_info'):
	file = open('/tmp/user_partition_info', 'r')
	for line in file.readlines():
		l = string.split(line)
		if len(l) == 2 and l[0] == 'stack':
			partscheme = l[1]
			break
	file.close()

	if partscheme != None:
		os.remove('/tmp/user_partition_info')

if partscheme == 'manual' or os.path.exists('/tmp/manual-partitioning'):
	#
	# manual partitioning, just touch a file
	#
	os.system('touch /tmp/manual-partitioning')
else:
	#
	# link into a class that has several disk helper functions
	#
	nodestorage = stack_partition.StackPartition()

	#
	# get the list of hard disks and software raid devices
	#
	cmd = '/sbin/mdadm --assemble --scan > /dev/null 2>&1'
	os.system(cmd)
	disks = nodestorage.getDisks()
	raids = nodestorage.getRaids()

	#
	# check if this is a frontend
	#
	file = open('/proc/cmdline', 'r')
	args = string.split(file.readline())
	file.close()

	if 'build' in args:
		parts = frontend(nodestorage, disks, raids)
	else:
		parts = backend(nodestorage, disks, raids)
		lvms = lvm(nodestorage)
		if lvms:
			parts += lvms

	for line in parts:
		print(line)

