#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import shlex
import subprocess
import sys
import os
import re

sys.path.append('/tmp')
from stack_site import *

sys.path.append('/opt/stack/lib')
from stacki_storage import *
from stacki_default_part import rhel
import stack

##
## globals
##
host_partitions = []
md_re = re.compile("^md[0-9]+$")
FNULL = open(os.devnull, 'w')


##
## Manual Partitioning
##
manual = False
if os.path.exists('/tmp/user_partition_info'):
	with open('/tmp/user_partition_info', 'r') as f:
		manual = 'manual' in f.read().split()
if manual:
	sys.exit(0)

##
## functions
##

def outputPartition(p, initialize):
	#
	# this function only outputs physical partitions, that is, ignore
	# software RAID and LVM definitions
	#
	output = []

	#
	# if there is no mountpoint and we are not creating this partition,
	# then there is nothing to do
	#
	mnt = p['mountpoint']
	if not mnt or mnt == 'None':
		mnt = None

	if not mnt or p['fstype'] == 'linux_raid_member':
		return []

	label = None
	primary = 0
	grow = 0
	partition_id = None

	fsargs = shlex.split(p['options'])
	for arg in fsargs:
		if '--label=' in arg:
			label = arg.split('=')[1]
		elif '--asprimary' in arg:
			primary = 1
		elif '--grow' in arg:
			grow = 1

	#
	# special case for '/', '/var' and '/boot', 'biosboot'
	#
	format = 0
	if initialize or mnt in [ '/', '/var', '/boot', 'biosboot' ]:
		format = 1

	line = [ 'part', mnt ]

	#
	# physical software RAID or LVM partitions, (e.g., 'raid', 'lvm')
	# don't have 'fstype' definitions
	#
	if p['fstype'] not in [ 'raid', 'lvm']:
		line += [ '--fstype=%s' % p['fstype'] ]

	if initialize:
		#
		# we are creating partitions, so we need 'size', 'ondisk',
		# and optionally 'asprimary'
		#
		if p['size'] == 0 or grow:
			line += [ '--size=1', '--grow' ]
		else:
			line += [ '--size=%d' % p['size'] ]

		line += [ '--ondisk=%s' % p['device'] ]

		if primary:
			line += [ '--asprimary' ]
	else:
		#
		# we are reusing partitions, so we only need 'onpart'
		#
		if 'uuid' in p:
			line += [ '--onpart=/dev/disk/by-uuid/%s' % p['uuid'] ]
		elif 'diskpart' in p:
			line += [ '--onpart=%s' % p['diskpart'] ]

	if not format:
		line += [ '--noformat' ]

	if label:
		line += [ '--label=%s' % label ]

	print('%s' % ' '.join(line))


def sortPartId(entry):
	#
	# make sure 'None' partid's go at the end of the list
	#
	try:
		key = entry['partid']
		if not key:
			key = sys.maxsize
	except:
		key = sys.maxint

	return key


def doPartitions(disk, initialize):
	import operator

	output = []

	if initialize:
		#
		# since we are wiping this disk, use the partitions from
		# the CSV
		#
		csv_partitions.sort(key = sortPartId)
		partitions = csv_partitions
	else:
		#
		# we are going to keep this disk intact, so just reconnect the
		# existing partitions -- that is, use the data that we read
		# off the installing system
		#
		partitions = host_partitions

	for p in partitions:
		if p['device'] != disk['device']:
			continue

		#
		# skip all software RAID partitions (e.g., md0, md1, etc.)
		#
		if 'diskpart' in p and md_re.match(p['diskpart']):
			continue

		outputPartition(p, initialize)

	return


def doOutputExistingLVM(name, fstab):

	p = subprocess.run([ '/sbin/lvs', '-o', 'vg_name,lv_name,dm_path', '--noheadings', '--separator=:' ],
			   stdin=subprocess.PIPE,
			   stdout=subprocess.PIPE,
			   stderr=subprocess.PIPE)

	for line in p.stdout.decode().split('\n'):
		l = line.split(':')
		if len(l) > 2:
			vgname = l[0].strip()
			if vgname == name:
				lvname = l[1].strip()
				dmpath = l[2].strip()

				for p in fstab:
					if p['device'] == dmpath:
						line = [ 'logvol' ]
						line += [ '%s' %
							p['mountpoint'] ]
						line += [ '--name=%s' %
							lvname ]
						line += [ '--vgname=%s' %
							vgname ]
						line += [ '--useexisting' ]
						if p['mountpoint'] not in [ '/', '/var', '/boot' ]:
							line += [ '--noformat' ]

						print('%s' % ' '.join(line))


def doOutputLVM(device, partitions):
	for p in partitions:
		if p['device'] == device:
			line = [ 'logvol' ]
			line += [ '%s' % p['mountpoint'] ]
			line += [ '--vgname=%s' % p['device'] ]
			line += [ '--fstype=%s' % p['fstype'] ]
			line += [ '%s' % p['options'] ]

			if p['size'] == 0:
				line += [ '--size=1', '--grow' ]
			else:
				line += [ '--size=%d' % p['size'] ]

			print('%s' % ' '.join(line))


def isNewRaid(disks, partitions, options):
	for o in options.split():
		for p in partitions:
			for disk in disks:
				if disk['device'] == p['device'] and \
						p['mountpoint'] == o and \
						disk['nuke']:
					return 1

	return 0


def isNewLVM(disks, partitions, mountpoint):
	for p in partitions:
		if p['mountpoint'] == mountpoint:
			if md_re.match(p['device']):
				#
				# if this LVM is on a software RAID, and if
				# one of the physical disks in the software
				# RAID is going to be nuked, then this will
				# be a new LVM
				#
				if isNewRaid(disks, partitions, p['options']):
					return 1

			else:
				for disk in disks:
					if disk['device'] == p['device'] and \
							disk['nuke']:
						return 1

	return 0


def doLVM(disks, partitions, fstab):
	#
	# an LVM definition is three lines in the 'partitions' dictionary:
	#
	#	1) a physical partition
	#	2) a volume group on the physical partition
	#	3) a file system on the volume group
	#
	# which look like:
	#
	#	1) physical partition:
	#
	#		'fstype': 'lvm',
	#		'device': 'sdb',
	#		'mountpoint': 'pv.01',
	#		'options': '--grow',
	#		'size': 1L
	#
	#	2) volume group:
	#
	#		'fstype': 'volgroup',
	#		'device': 'pv.01',
	#		'mountpoint': 'volgrp01',
	#		'size': 0L
	#
	#	3) file system (a.k.a. volume):
	#		'fstype': 'xfs',
	#		'device': 'volgrp01',
	#		'mountpoint': '/var/lib/mysql',
	#		'options': '--name=mysql_libs',
	#

	for p in partitions:
		if p['fstype'] == 'volgroup':
			#
			# determine if the disk that this volume group is
			# supposed to be on has been nuked -- that is, should
			# we create a new LVM or should we reconnect an
			# existing LVM
			#
			is_new_lvm = isNewLVM(disks, partitions, p['device'])

			if is_new_lvm:
				print('volgroup %s %s' % (p['mountpoint'], p['device']))

				#
				# the 'mountpoint' in the 'volgroup'
				# definition is the 'device' in the file
				# system definition that maps to this LVM
				#
				doOutputLVM(p['mountpoint'], partitions)
			else:
				doOutputExistingLVM(p['mountpoint'], fstab)


def getMDInfo(device):

	p = subprocess.run([ 'mdadm', '--detail', '--export', '/dev/%s' % device ],
			   stdin=subprocess.PIPE,
			   stdout=subprocess.PIPE,
			   stderr=subprocess.PIPE)

	for line in p.stdout.decode().split('\n'):
		l = line.split('=')

		if l[0] == 'MD_DEVNAME':
			return l[1]

	return None


def doRAID(csv_partitions, host_partitions):
	#
	# a RAID definition is at least three entries in the 'partitions'
	# dictionary:
	#
	#	1) two or more physical partitions
	#	2) a 'device' field with the format 'md*'
	#
	# which look like:
	#
	#	1) physical partition:
	#
	#		'fstype': 'raid',
	#		'device': 'sda',
	#		'mountpoint': 'raid.01',
	#		'options': '',
	#		'size': 16000L
	#
	#	2) 'md*' entry
	#
	#		'fstype': 'ext4',
	#		'device': 'md0',
	#		'mountpoint': '/',
	#		'options':'--level=RAID1 raid.01 raid.02',
	#		'size': 0L
	#

	#
	# first reconnect all existing RAIDs
	#
	existing = []
	for p in host_partitions:
		if 'diskpart' in p and md_re.match(p['diskpart']) and p['diskpart'] not in existing:

			existing.append(p['diskpart'])

			#
			# don't reconnect this software RAID if there is
			# no mountpoint -- that is case when the software RAID
			# is used by an LVM volume
			#
			if not p['mountpoint']:
				continue

			mdname = getMDInfo(p['diskpart'])

			line = [ 'raid' ]
			line += [ '%s' % p['mountpoint'] ]

			#
			# make sure the '=' is not present -- it causes a
			# failure in Anaconda
			#
			if mdname:
				line += [ '--device=%s' % mdname ]
			else:
				line += [ '--device=%s' % p['device'] ]

			if p['mountpoint'] not in [ '/', '/var', '/boot' ]:
				line += [ '--noformat' ]

			line += [ '--useexisting' ]

			print('%s' % ' '.join(line))

	for p in csv_partitions:
		if md_re.match(p['device']) and p['device'] not in existing:
			line = [ 'raid' ]
			line += [ '%s' % p['mountpoint'] ]

			#
			# make sure the '=' is not present -- it causes a
			# failure in Anaconda
			#
			if p['fstype'] != 'lvm':
				line += [ '--fstype %s' % p['fstype'] ]

			line += [ '--device %s' % p['device'] ]
			line += [ '%s' % p['options'] ]

			print('%s' % ' '.join(line))

##
## MAIN
##
if 'nukecontroller' in attributes:
	nukecontroller = attributes['nukecontroller']
else:
	nukecontroller = 'false'

if 'nukedisks' in attributes:
	n = attributes['nukedisks']

	#
	# if 'nukedisks' is a boolean, convert it to list with the '*' entry
	#
	if n and n.upper() in [ 'ALL', 'YES', 'Y', 'TRUE', '1' ]:
		nukedisks = [ '*' ]
	else:
		nukedisks = n.split()
else:
	nukedisks = []

disks = getHostDisks(nukedisks)

#
# make a list of all possible locations for /etc/fstab:
#
#	1) look on all physical partitions
#	2) look on all software RAID devices
#	3) look on all LVM volumes
#

#
# first try to find /etc/fstab on all the physical partitions
#
devices = getDeviceList(disks)

host_fstab = getHostFstab(devices)

host_partitions = getHostPartitions(disks, host_fstab)

# print 'host_fstab : %s' % host_fstab
# print
# print 'host_partitions : %s' % host_partitions
# print

frontend = False
with open('/proc/cmdline','r') as f:
	frontend = 'frontend' in f.read().split()

if not csv_partitions:
	parts = []
	# on a frontend, get 'release' from the stack module
	release = attributes.get('release', stack.release)
	if os.path.exists('/sys/firmware/efi'):
		default = 'uefi'
	else:
		default = 'default'

	ostype = 'rhel7'

	var = '%s_%s' % (ostype, default)
	if hasattr(rhel, var):
		parts = getattr(rhel, var)
	else:
		parts = getattr(rhel, 'default')

	if 'boot_device' in attributes:
		bootdisk = attributes['boot_device']
	else:
		bootdisk = disks[0]['device']
		nuke_bootdisk = True
		for part in host_partitions:
			if part['mountpoint'] == '/':
				bootdisk = part['device']
				nuke_bootdisk = False
				break
		if nuke_bootdisk:
			disks[0]['nuke'] = 1


	csv_partitions = []
	partid = 1

	for m, s, f in parts:
		csv_partitions.append(
			{
				'partid': partid,
				'scope': 'global',
				'device': bootdisk,
				'mountpoint': m,
				'size': s,
				'fstype': f,
				'options': ''
			})

		partid += 1

#
# there are 2 scenarios:
#
#	1) nukedisks == true
#	2) nukedisks == false
#
# 1 is easy -- nuke the disks and recreate the partitions specified in the
# "partitions" variable
#
# For 2, reformat "/", "/boot" (if present) and "/var" on the boot disk, then
# reconnect all other discovered partitions.
#

#
# Also, for Red Hat, we need to output the disk partition configuration in
# this order:
#
#	1) all the physical partitions
#	2) all the software RAID definitions
#	3) all the LVM definitions
#

#
# process all nuked disks first
#
initialize = 1
for disk in disks:
	if disk['nuke']:
		doPartitions(disk, initialize)

#
# now process all non-nuked disks
#
initialize = 0
for disk in disks:
	if not disk['nuke']:
		doPartitions(disk, initialize)

#
# process software RAID
#
doRAID(csv_partitions, host_partitions)

#
# process LVM
#
doLVM(disks, csv_partitions, host_fstab)

