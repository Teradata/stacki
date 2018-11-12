#!/opt/stack/bin/python

import shlex
import subprocess
import sys
import os

sys.path.append('/tmp')
from stack_site import *

##
## globals
##
host_partitions = []

##
## functions
##

def getNukes(host_disks, s):
	disks = []

	if s and s.upper() in [ 'ALL', 'YES', 'Y', 'TRUE', '1' ]:
		disks = host_disks
	elif s and s.upper() in ['NONE', 'NO', 'N', 'FALSE', '0' ]:
                disks = []
	elif s:
		#
		# validate the user input for nukedisks -- that is, make sure 
		# the disks specified by the user are actually on this machine
		#
		for disk in s.split():
			if disk in host_disks:
				disks.append(disk)

	return disks


def nukeIt(disk):
	#
	# Clear out the master boot record of the drive
	#
	FNULL = open(os.devnull, 'w')

	if attributes.has_key('disklabel'):
		disklabel = attributes['disklabel']
	else:
		disklabel = 'gpt'

        cmd = 'dd if=/dev/zero of=/dev/%s count=512 bs=1' % disk
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)

	cmd = 'parted -s /dev/%s mklabel %s' % (disk, disklabel)
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)

	FNULL.close()
	return


def outputPartition(p, initialize):
	xml_partitions = []

	if initialize == 'true':
		create = 'true'
	else:
		create = 'false'

	#
	# if there is no mountpoint and we are not creating this partition,
	# then there is nothing to do
	#
	mnt = p['mountpoint']
	if not mnt or mnt == 'None':
		mnt = None

	if create == 'false' and not mnt:
		return xml_partitions

	#
	# special case for '/', '/var' and '/boot'
	#
	if mnt in [ '/', '/var', '/boot' ]:
		format = 'true'
	else:
		if initialize == 'true':
			format = 'true'
		else:
			format = 'false'

	xml_partitions.append('\t\t\t<partition>')
	xml_partitions.append('\t\t\t\t<create config:type="boolean">%s</create>' % create)

	if mnt:
		xml_partitions.append('\t\t\t\t<mount>%s</mount>' % mnt)

	if create == 'true':
		if p['size'] == 0:
			xml_partitions.append('\t\t\t\t<size>max</size>')
		else:
			xml_partitions.append('\t\t\t\t<size>%dM</size>' % p['size'])

	if p['fstype']:
		xml_partitions.append('\t\t\t\t<filesystem config:type="symbol">%s</filesystem>' % p['fstype'])
		xml_partitions.append('\t\t\t\t<format config:type="boolean">%s</format>' % format)

	#
	# see if there is a label or 'asprimary' associated with this partition
	#
	label = None
	primary = 'false'

	fsargs = shlex.split(p['options'])
	for arg in fsargs:
		if '--label=' in arg:
			label = arg.split('=')[1]
		elif '--asprimary' in arg:
			primary = 'true'

	if primary == 'true' or (mnt in [ '/', '/boot' ] and create == 'true'):
		xml_partitions.append('\t\t\t\t<partition_type>primary</partition_type>')

	if label:
		xml_partitions.append('\t\t\t\t<label>%s</label>' % label)

		if mnt:
			xml_partitions.append('\t\t\t\t<mountby config:type="symbol">label</mountby>')
	else:
		if mnt:
			xml_partitions.append('\t\t\t\t<mountby config:type="symbol">uuid</mountby>')

		if format == 'false' and p.has_key('uuid'):
			xml_partitions.append('\t\t\t\t<uuid>%s</uuid>' % p['uuid'])
		elif format == 'true' and create == 'false' \
				and p.has_key('partnumber'):

			#
			# we are reusing a partition, and we are reformatting
			# it which will create a new UUID, so we need to tell
			# the installer which physical partition this mountpoint
			# is associated with
			#
			xml_partitions.append('\t\t\t\t<partition_nr config:type="integer">%s</partition_nr>' % p['partnumber'])
		
	xml_partitions.append('\t\t\t</partition>')

	return xml_partitions


def sortPartId(entry):
	#
	# make sure 'None' partid's go at the end of the list
	#
	try:
		key = entry['partid']
		if not key:
			key = sys.maxint
	except:
		key = sys.maxint

	return key


def doPartitions(disk, initialize):
	import operator

	xml_partitions = []

	if initialize == 'true':
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
		if p['device'] != disk:
			continue

		xml_part = outputPartition(p, initialize)
		if xml_part:
			xml_partitions += xml_part

	return xml_partitions


def outputDisk(disk, initialize):
	xml_partitions = doPartitions(disk, initialize)

	#
	# only output XML configuration for this disk if there is partitioning
	# configuration for this disk
	#
	if xml_partitions:
		if attributes.has_key('disklabel'):
			disklabel = attributes['disklabel']
		else:
			disklabel = 'gpt'

		print '\t<drive>'
		print '\t\t<device>/dev/%s</device>' % disk
		print '\t\t<disklabel>%s</disklabel>' % disklabel
		print '\t\t<initialize config:type="boolean">%s</initialize>' % initialize
		print ''

		print '\t\t<partitions config:type="list">'
		for p in xml_partitions:
			print '%s' % p
		print '\t\t</partitions>'

		print '\t</drive>'

	return


def getHostDisks():
	"""Returns list of disks on this machine"""

	disks = []
	p = subprocess.Popen([ 'lsblk', '-nio', 'NAME,RM,RO' ],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	out = p.communicate()[0]
	
	for l in out.split('\n'):
		# Ignore empty lines
		if not l.strip():
			continue

		#
		# Skip read-only and removable devices
		#
		arr = l.split()
		removable = arr[1].strip()
		readonly  = arr[2].strip()

		if removable == "1" or readonly == "1":
			continue

		diskname = arr[0].strip()

		if diskname[0] in [ '|' , '`' ]:
			continue

		disks.append(diskname)

	return disks


def getHostPartitionDevices(disk):
	"""
	Returns the device names of all the partitions on a specific disk
	"""

	devices = []
	p = subprocess.Popen([ 'lsblk', '-nrio', 'NAME', '/dev/%s' % disk ],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	out = p.communicate()[0]
	
	for l in out.split('\n'):
		# Ignore empty lines
		if not l.strip():
			continue

		#
		# Skip read-only and removable devices
		#
		arr = l.split()
		diskname = arr[0].strip()

		if diskname != disk:
			devices.append(diskname)

	return devices


def getHostMountpoint(host_fstab, uuid, label):
	for part in host_fstab:
		if part['device'] == 'UUID=%s' % uuid:
			return part['mountpoint']
		elif part['device'] == 'LABEL=%s' % label:
			return part['mountpoint']

	return None


def getDiskPartNumber(disk):
	partnumber = 0

	p = subprocess.Popen([ 'blkid', '-o', 'export',
		'-s', 'PART_ENTRY_NUMBER', '-p', '/dev/%s' % disk ],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	out = p.communicate()[0]

	#
	# the above should only return one line
	#
	arr = out.split('=')

	if len(arr) == 2:
		partnumber = arr[1].strip()

	return partnumber


def getHostPartitions(host_disks, host_fstab):
	for disk in host_disks:
		p = subprocess.Popen([ 'lsblk', '-nrbo', 
			'NAME,SIZE,UUID,LABEL,MOUNTPOINT,FSTYPE',
			'/dev/%s' % disk ],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
		out = p.communicate()[0]
		
		for l in out.split('\n'):
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

			partnumber = getDiskPartNumber(diskname)

			disk_partitions = {}
			disk_partitions['device'] = disk
			disk_partitions['mountpoint'] = mountpoint
			disk_partitions['size'] = size
			disk_partitions['fstype'] = fstype
			disk_partitions['uuid'] = uuid

			if partnumber:
				disk_partitions['partnumber'] = partnumber

			if label:
				disk_partitions['options'] = \
					'--label=%s' % label
			else:
				disk_partitions['options'] = ''

			host_partitions.append(disk_partitions)

	return host_partitions


def getHostFstab(disks):
	"""Get contents of /etc/fstab by mounting all disks
	and checking if /etc/fstab exists.
	"""

	import tempfile

	host_fstab = []

	mountpoint = tempfile.mktemp()
	os.makedirs(mountpoint)
	fstab = mountpoint + '/etc/fstab'

	for disk in disks:
		#
		# Let's go look at all the disks for /etc/fstab
		#
		for d in getHostPartitionDevices(disk):
			os.system('mount /dev/%s %s' % (d, mountpoint) + \
				' > /dev/null 2>&1')

			if os.path.exists(fstab):
				file = open(fstab)

				for line in file.readlines():
					entry = {}

					l = line.split()
					if len(l) < 3:
						continue

					entry['device'] = l[0].strip()
					entry['mountpoint'] = l[1].strip()
					entry['fstype'] = l[2].strip()

					host_fstab.append(entry)

				file.close()

			os.system('umount %s 2> /dev/null' % (mountpoint))

			if host_fstab:
				break
		if host_fstab:
			break

	try:
		os.removedirs(mountpoint)
	except:
		pass

	return host_fstab

##
## MAIN
##

host_disks = getHostDisks()
host_fstab = getHostFstab(host_disks)
host_partitions = getHostPartitions(host_disks, host_fstab)

#print '<?xml version="1.0"?>'
#print ''
#print '<partitioning xmlns="http://www.suse.com/1.0/yast2ns" xmlns:config="http://www.suse.com/1.0/configns" config:type="list">'

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

if attributes.has_key('nukedisks'):
	nukedisks = attributes['nukedisks']
else:
	nukedisks = 'false'

#
# process all nuked disks first
#
nukelist = getNukes(host_disks, nukedisks)

for disk in nukelist:
	print("nuking %s" % disk)
	nukeIt(disk)

#	initialize = 'true'
#	outputDisk(disk, initialize)

#
# now process all non-nuked disks
#
#initialize = 'false'
#for disk in host_disks:
#	if disk not in nukelist:
#		outputDisk(disk, initialize)	

#print '</partitioning>'
#print ''

