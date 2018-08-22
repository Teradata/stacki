#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import shlex
import subprocess
import sys
import os
import time

sys.path.append('/tmp')
from stack_site import attributes

sys.path.append('/opt/stack/lib')
from stacki_storage import attr2bool, getHostDisks, getDeviceList, getHostFstab, getHostPartitions

##
## globals
##
FNULL = open(os.devnull, 'w')

##
## functions
##

def nukeLVM(volumegroup):
	for (display, remove) in [
			('lvdisplay --all -c', 'lvremove --force'),
			('vgdisplay -c', 'vgremove --force'),
			('pvdisplay -c', 'pvremove --force') ]:

		p = subprocess.run(shlex.split(display),
				   stdout = subprocess.PIPE, 
				   stderr = FNULL)
		for line in p.stdout.decode().split():
			l = line.split(':')
			if len(l) > 1 and (volumegroup == '*' or
					volumegroup == l[1]):

				target = l[0]
				cmd = '%s %s' % (remove, target)
				subprocess.call(shlex.split(cmd),
					stdout = FNULL,
					stderr = subprocess.STDOUT)

def stopMD():
	#
	# we need to stop all MDs before we can remove them
	#
	cmd = 'mdadm --stop --scan'
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)


def nukeMD(part):
	cmd = 'mdadm --zero-superblock /dev/%s' % part
	subprocess.call(shlex.split(cmd), stdout = FNULL,
		stderr = subprocess.STDOUT)


def nukeDisk(disk):
	if 'disklabel' in attributes:
		disklabel = attributes['disklabel']
	else:
		disklabel = 'gpt'

	#
	# Clear out the master boot record of the drive
	#
	cmd = 'dd if=/dev/zero of=/dev/%s count=512 bs=1' % disk
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)

	cmd = 'parted -s /dev/%s mklabel %s' % (disk, disklabel)
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)

	return

#
# MAIN
#

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
	elif n and n.upper() in [ 'NONE', 'NO', 'N', 'FALSE', '0' ]:
		nukedisks = 'false'
	else:
		nukedisks = n.split()
else:
	nukedisks = 'false'

if not attr2bool(nukedisks):

	disks = getHostDisks(nukedisks)
	devicelist = getDeviceList(disks)
	host_fstab = getHostFstab(devicelist)
	partitions = getHostPartitions(disks, host_fstab)
	if not partitions:
		nukedisks = ['*']
	else:
		slash_found = False
		for part in partitions:
			if part['mountpoint'] == '/':
				slash_found = True
				break
		if not slash_found:
			nukedisks = [ disks[0] ]

if not attr2bool(nukecontroller) and not attr2bool(nukedisks):
	#
	# nothing to do, so let's exit
	#
	sys.exit(0)

#
# if 'nukecontroller' is true, then the assumption is that all data on the
# disks will no longer be accessible, therefore, nuke all disks
#
if attr2bool(nukecontroller):
	nukedisks = [ '*' ]

disks = getHostDisks(nukedisks)
count = 10
# Wait until we have disk info from the storage controller
while count > 0:
	if len(disks) == 0:
		time.sleep(2)
		count -= 1
		disks = getHostDisks(nukedisks)
	else:
		break

#
# nuke LVM first
#
lvms = []
for disk in disks:
	for lvm in disk['lvm']:
		#
		# determine if the disk this volume is on will be nuked. if
		# not, then do nothing and continue, that is, we'll preserve
		# this volume
		#
		if not disk['nuke']:
			continue

		#
		# an LVM reported by getHostDisks() has the format:
		#
		#	volumegroupname-mountpoint
		#
		# let's strip out the volumegroupname
		#
		volumegroup = lvm.split('-')[0]
		
		if volumegroup not in lvms:
			nukeLVM(volumegroup)
			lvms.append(volumegroup)

#
# nuke software RAID devices next
#
stopMD()

mds = []
for disk in disks:
	#
	# if there is at least one RAID associated with this disk and if this
	# disk is marked to be nuked, then we can nuke the RAID on all
	# partitions on the disk (i.e., zero the MD superblock for each
	# partition) because the entire disk is going to reformatted anyway.
	#
	if len(disk['raid']) and disk['nuke']:
		for part in disk['part']:
			nukeMD(part)

#
# lastly, nuke the physical disk master boot record
#
for disk in disks:
	if disk['nuke']:
		nukeDisk(disk['device'])

