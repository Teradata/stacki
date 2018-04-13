#!/opt/stack/bin/python3 -E

import shlex
import subprocess
import sys
import os
import time

sys.path.append('/tmp')
from stack_site import attributes, csv_partitions

sys.path.append('/opt/stack/lib')
from stacki_default_part import sles

import stack

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

	if 'disklabel' in attributes:
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

	if initialize.lower() == 'true':
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
	if mnt in [ '/', '/var', '/boot', '/boot/efi' ]:
		format = 'true'
	else:
		if initialize.lower() == 'true':
			format = 'true'
		else:
			format = 'false'

	xml_partitions.append('\t\t\t<partition>')

	if initialize.lower() == 'true':
		xml_partitions.append('\t\t\t\t<create config:type="boolean">%s</create>' % create)

	if mnt:
		xml_partitions.append('\t\t\t\t<mount>%s</mount>' % mnt)

	if create == 'true':
		if p['size'] == 0:
			xml_partitions.append('\t\t\t\t<size>max</size>')
		else:
			xml_partitions.append('\t\t\t\t<size>%dM</size>' %  p['size'])

	if p['fstype']:
		if initialize.lower() == 'true':
			xml_partitions.append('\t\t\t\t<filesystem config:type="symbol">%s</filesystem>' % p['fstype'])
		xml_partitions.append('\t\t\t\t<format config:type="boolean">%s</format>' % format)

	#
	# see if there is a label or 'asprimary' associated with this partition
	#
	label = None
	primary = 'false'
	partition_id = None

	fsargs = shlex.split(p['options'])
	for arg in fsargs:
		if '--label=' in arg:
			label = arg.split('=')[1]
		elif '--asprimary' in arg:
			primary = 'true'
		elif '--partition_id=' in arg:
			partition_id = arg.split('=')[1]

	if mnt == '/':
		if not label:
			label = "rootfs"

	if primary == 'true' or (mnt in [ '/', '/boot', '/boot/efi' ] and create == 'true'):
		xml_partitions.append('\t\t\t\t<partition_type>primary</partition_type>')

	if create == 'true' and partition_id:
		xml_partitions.append('\t\t\t\t<partition_id config:type="integer">%s</partition_id>' % partition_id)

	if label:
		xml_partitions.append('\t\t\t\t<label>%s</label>' % label)

		if mnt:
			xml_partitions.append('\t\t\t\t<mountby config:type="symbol">label</mountby>')
	else:
		if mnt:
			xml_partitions.append('\t\t\t\t<mountby config:type="symbol">uuid</mountby>')

		if format == 'false' and 'uuid' in p:
			xml_partitions.append('\t\t\t\t<uuid>%s</uuid>' % p['uuid'])
		elif format == 'true' and create == 'false' \
				and 'partnumber' in p:

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

	if initialize.lower() == 'true':
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
	if xml_partitions and initialize.lower() == 'true':
		if 'disklabel' in attributes:
			disklabel = attributes['disklabel']
		else:
			disklabel = 'gpt'

		print('\t<drive>')
		print('\t\t<device>/dev/%s</device>' % disk)
		print('\t\t<disklabel>%s</disklabel>' % disklabel)
		print('\t\t<initialize config:type="boolean">%s</initialize>' % initialize)
		print('')

		print('\t\t<partitions config:type="list">')
		for p in xml_partitions:
			print('%s' % p)
		print('\t\t</partitions>')

		print('\t</drive>')
	elif xml_partitions and initialize.lower() == 'false':
		if 'disklabel' in attributes:
			disklabel = attributes['disklabel']
		else:
			disklabel = 'gpt'
		print('\t<fstab>')
		print('\t\t<use_existing_fstab config:type="boolean">true</use_existing_fstab>')
		print('\t\t<partitions config:type="list">')
		for p in xml_partitions:
			print('%s' % p)
		print('\t\t</partitions>')
		print('\t</fstab>')

	return


def getHostDisks():
	"""Returns list of disks on this machine"""

	disks = []
	p = subprocess.Popen([ 'lsblk', '-nio', 'NAME,RM,RO' ],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	o = p.communicate()[0]
	out = o.decode()
	
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
	o = p.communicate()[0]
	out = o.decode()
	
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
	o = p.communicate()[0]
	out = o.decode()

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
		o = p.communicate()[0]
		out = o.decode()
		
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

count = 5
while count > 0:
	if len(host_disks) == 0:
		time.sleep(1)
		count = count - 1
		host_disks = getHostDisks()
	else:
		break

host_fstab = getHostFstab(host_disks)
host_partitions = getHostPartitions(host_disks, host_fstab)

if not csv_partitions:
	parts = []
	if attributes['os.version'] == "11.x" and attributes['os'] == "sles":
		ostype = "sles11"
	elif attributes['os.version'] == "12.x" and attributes['os'] == "sles":
		ostype = "sles12"
	else:
		# Give ostype some default
		ostype = "sles11"

	if os.path.exists('/sys/firmware/efi'):
		default = 'uefi'
	else:
		default = 'default'

	var = '%s_%s' % (ostype, default)
	if hasattr(sles, var):
		parts = getattr(sles, var)
	else:
		parts = getattr(sles, 'default')

	if 'boot_device' in attributes:
		bootdisk = attributes['boot_device']
	else:
		bootdisk = host_disks[0]

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

print('<?xml version="1.0"?>')
print('')

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
# if host_fstab is an empty list, turning on nukedisks=true" to avoid SLES defaults
if host_fstab == []:
	nukedisks = 'true'
elif 'nukedisks' in attributes:
	nukedisks = attributes['nukedisks']
else:
	nukedisks = 'false'

if nukedisks.lower() == 'true':
	print('<partitioning xmlns="http://www.suse.com/1.0/yast2ns" xmlns:config="http://www.suse.com/1.0/configns" config:type="list">')
else:
	print('<partitioning_advanced xmlns="http://www.suse.com/1.0/yast2ns" xmlns:config="http://www.suse.com/1.0/configns">')


#
# process all nuked disks first
#
nukelist = getNukes(host_disks, nukedisks)

for disk in nukelist:
	nukeIt(disk)

	initialize = 'true'
	outputDisk(disk, initialize)

#
# now process all non-nuked disks
#
initialize = 'false'
for disk in host_disks:
	if disk not in nukelist:
		outputDisk(disk, initialize)	


if nukedisks.lower() == 'true':
	print('</partitioning>')
else:
	print('</partitioning_advanced>')
print('')