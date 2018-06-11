#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
"""Output the /tmp/partition.xml for autoyast to create the partitions as requested.

When we do a fresh install, the fix_fstab.py and fix_partition.py are not needed

When we want to do a reinstall and keep data disks (nukedisks=False) we need to utilize the previous fstab.
The fix_fstab.py runs during install-post to gather data for fix_partitions.py and edit the /mnt/etc/fstab file
The fix_partitions.py runs during F10-a-fix-partitions to edit the partition labels as needed to match the new
/mnt/etc/fstab.
Called Python with -E, as that's super subtle
"""
import shlex
import subprocess
import sys
import os
import time
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom
from shutil import copy
sys.path.append('/tmp')
from stack_site import attributes, csv_partitions
sys.path.append('/opt/stack/lib')
from stacki_default_part import sles
from stack.bool import str2bool


#
# globals
#
host_partitions = []
fs_info = "/tmp/fstab_info"
partitioning_config = ElementTree.Element("partitioning")
partitioning_config.set('xmlns', "http://www.suse.com/1.0/yast2ns")
partitioning_config.set('xmlns:config', 'http://www.suse.com/1.0/configns')
partitioning_config.set('config:type', 'list')
#
# functions
#


def get_nukes(host_disks, to_nuke, nuke_list):
	"""Return a list of disks to nuke, as the use may want to nuke /dev/sdc, but not /dev/sdb."""
	disks = []

	if to_nuke:
		disks = host_disks
	elif not to_nuke:
		# validate the user input for nuke_list -- that is, make sure
		# the disks specified by the user are actually on this machine
		for disk in nuke_list.split():
			if disk in host_disks:
				disks.append(disk)
		# If the nuke_list = false, 0, FALSE, etc;
		# then no matches will be found and empty list returned

	return disks


def nuke_it(disk):
	""" Clear out the master boot record of the drive."""
	dev_null = open(os.devnull, 'w')

	if 'disklabel' in attributes:
		disklabel = attributes['disklabel']
	else:
		disklabel = 'gpt'

	cmd = 'dd if=/dev/zero of=/dev/%s count=512 bs=1' % disk
	subprocess.call(shlex.split(cmd), stdout=dev_null, stderr=subprocess.STDOUT)

	cmd = 'parted -s /dev/%s mklabel %s' % (disk, disklabel)
	subprocess.call(shlex.split(cmd), stdout=dev_null, stderr=subprocess.STDOUT)

	dev_null.close()
	return


def partition_init_path(element_partition, initialize, partition, partition_id):
	"""Determine XML for properties involving drive being formatted.

	If not being formatted, it still adds the create false tag."""
	element_create = ElementTree.SubElement(element_partition, 'create')
	element_create.text = '%s' % str(initialize).lower()
	element_create.set('config:type', 'boolean')

	if initialize:
		if partition['size'] == 0:
			ElementTree.SubElement(element_partition, 'size').text = 'max'
		else:
			ElementTree.SubElement(element_partition, 'size').text = '%dM' % partition['size']

	if initialize and partition_id:
		element_partition_id = ElementTree.SubElement(element_partition, 'partition_id')
		element_partition_id.text = '%s' % partition_id
		element_partition_id.set('config:type', 'integer')


def partition_mount_label(element_partition, initialize, partition, mnt, label):
	"""Determine XML properties for partition mounted by label.

	Note: Label does not work if formatting partition, but not initializing drive, as label is lost during reformat,
	even if specified. Using fix_fstab.py + fix_partition.py corrects this issue"""
	if mnt:
		element_mountby = ElementTree.SubElement(element_partition, 'mountby')
		element_mountby.text = 'label'
		element_mountby.set('config:type', 'symbol')
	if initialize:
		ElementTree.SubElement(element_partition, 'label').text = '%s' % label
	else:
		element_partition_nr = ElementTree.SubElement(element_partition, 'partition_nr')
		element_partition_nr.text = '%s' % partition['partnumber']
		element_partition_nr.set('config:type', 'integer')


def partition_mount_uuid(element_partition, initialize, partition, mnt, format_partition):
	"""Determine XML properties for partition mounted by UUID.

	Used when no label is provided. If Autoyast is left to its own devices it will use /dev/disk/by-id/, which is not
	preferred. Although fix_fstab.py and fix_partition.py should be able to handle this scenario.
	"""
	if mnt:
		element_mountby = ElementTree.SubElement(element_partition, 'mountby')
		element_mountby.text = 'uuid'
		element_mountby.set('config:type', 'symbol')

	if not format_partition and 'uuid' in partition:
		ElementTree.SubElement(element_partition, 'uuid').text = '%s' % partition['uuid']
	elif format_partition and not initialize and 'partnumber' in partition:
		#
		# we are reusing a partition, and we are reformatting
		# it which will create a new UUID, so we need to tell
		# the installer which physical partition this mountpoint
		# is associated with
		#
		element_partition_nr = ElementTree.SubElement(element_partition, 'partition_nr')
		element_partition_nr.text = '%s' % partition['partnumber']
		element_partition_nr.set('config:type', 'integer')


def partition_fs_type(element_partition, partition, format_partition):
	"""Determine XML filesystem type to format the partition to."""
	if format_partition:
		element_filesystem = ElementTree.SubElement(element_partition, 'filesystem')
		element_filesystem.text = '%s' % partition['fstype']
		element_filesystem.set('config:type', 'symbol')

	element_format = ElementTree.SubElement(element_partition, 'format')
	element_format.text = '%s' % str(format_partition).lower()
	element_format.set('config:type', 'boolean')


def output_partition(partition, initialize, element_partition_list):
	"""Build partition xml for the partition provided.
	Return True if there is enough data to build partition, else return False"""
	#
	# if there is no mountpoint and we are not creating this partition,
	# then there is nothing to do
	#
	mnt = partition['mountpoint']
	if not mnt or mnt == 'None':
		mnt = None

	if not initialize and not mnt:
		return False
	#
	# see if there is a label or 'asprimary' associated with this partition
	#
	label = None
	primary = False
	partition_id = None

	fsargs = shlex.split(partition['options'])
	for arg in fsargs:
		if '--label=' in arg:
			label = arg.split('=')[1]
		elif '--asprimary' in arg:
			primary = True
		elif '--partition_id=' in arg:
			partition_id = arg.split('=')[1]

	if mnt == '/':
		if not label:
			label = "rootfs"
	#
	# special case for '/', '/var' and '/boot'
	#
	if mnt in ['/', '/var', '/boot', '/boot/efi']:
		format_partition = True
	else:
		format_partition = initialize
	element_partition = ElementTree.SubElement(element_partition_list, 'partition')
	partition_init_path(element_partition, initialize, partition, partition_id)
	if mnt:
		ElementTree.SubElement(element_partition, 'mount').text = '%s' % mnt
	if partition['fstype']:
		partition_fs_type(element_partition, partition, format_partition)
	if primary or (mnt in ['/', '/boot', '/boot/efi'] and initialize):
		ElementTree.SubElement(element_partition, 'partition_type').text = 'primary'
	# If we are formatting the partition, and not initializing the whole drive, use UUID instead of label.
	# Autoyast tries to use the old label for bootloader, after it already formatted and removed the label.
	if label and not (format_partition and not initialize):
		partition_mount_label(element_partition, initialize, partition, mnt, label)
	else:
		partition_mount_uuid(element_partition, initialize, partition, mnt, format_partition)
	return len(element_partition) > 0


def sort_part_id(entry):
	""" make sure 'None' partid's go at the end of the list"""
	try:
		key = entry['partid']
		if not key:
			key = sys.maxint
	except:
		key = sys.maxint

	return key


def do_partitions(disk, initialize, element_partition_list):
	"""Determine how to output the partition xml for the disk provided.
	If any partitions can be created for the disk, return True"""
	partitions_exist = []

	if initialize:
		#
		# since we are wiping this disk, use the partitions from
		# the CSV
		#
		csv_partitions.sort(key=sort_part_id)
		partitions = csv_partitions
	else:
		#
		# we are going to keep this disk intact, so just reconnect the
		# existing partitions -- that is, use the data that we read
		# off the installing system
		#
		partitions = host_partitions

	for each_partition in partitions:
		if each_partition['device'] != disk:
			continue
		partitions_exist.append(output_partition(each_partition, initialize, element_partition_list))
		# print(ElementTree.tostring(partitioning_config).decode())
	return any(partitions_exist)


def output_disk(disk, initialize):
	"""Output the disk and partition xml for the disk provided."""
	if 'disklabel' in attributes:
		disklabel = attributes['disklabel']
	else:
		disklabel = 'gpt'
	element_drive = ElementTree.SubElement(partitioning_config, 'drive')
	ElementTree.SubElement(element_drive, 'device').text = '/dev/%s' % disk
	ElementTree.SubElement(element_drive, 'disklabel').text = '%s' % disklabel
	element_init = ElementTree.SubElement(element_drive, 'initialize')
	element_init.text = '%s' % str(initialize).lower()
	element_init.set('config:type', 'boolean')
	element_partition_list = ElementTree.SubElement(element_drive, 'partitions')
	element_partition_list.set('config:type', 'list')

	if not do_partitions(disk, initialize, element_partition_list):
		# only output XML configuration for this disk if there is partitioning
		# configuration for this disk
		partitioning_config.remove(element_drive)

	return


def get_host_disks():
	"""Returns list of disks on this machine"""

	disks = []
	cmd = ['lsblk', '-nio', 'NAME,RM,RO']
	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
		readonly = arr[2].strip()

		if removable == "1" or readonly == "1":
			continue

		diskname = arr[0].strip()

		if diskname[0] in ['|', '`']:
			continue

		disks.append(diskname)

	return disks


def get_host_partition_devices(disk):
	"""
	Returns the device names of all the partitions on a specific disk
	"""

	devices = []
	cmd = ['lsblk', '-nrio', 'NAME', '/dev/%s' % disk]
	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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


def get_host_mount_point(host_fstab, uuid, label):
	"""Determine how the disk will be mounted, via UUID, LABEL, or not mounted."""
	for part in host_fstab:
		if part['device'] == 'UUID=%s' % uuid:
			return part['mountpoint']
		elif part['device'] == 'LABEL=%s' % label:
			return part['mountpoint']

	return None


def get_disk_part_number(partition_device):
	"""Return the partition number for the provided partition."""
	cmd = ['blkid', '-o', 'export', '-s', 'PART_ENTRY_NUMBER', '-p', '/dev/%s' % partition_device]
	p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o = p.communicate()[0]
	out = o.decode()

	for line in out.splitlines():
		if "PART_ENTRY_NUMBER" in line:
			arr = line.split('=')
			if len(arr) == 2:
				partnumber = arr[1].strip()
				return partnumber


def get_host_partitions(host_disks, host_fstab):
	"""Determine the partition info for the existing partition on the host's attached disks."""
	for disk in host_disks:
		cmd = ['lsblk', '-nrbo', 'NAME,SIZE,UUID,LABEL,MOUNTPOINT,FSTYPE', '/dev/%s' % disk]
		p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		o = p.communicate()[0]
		out = o.decode()
		
		for l in out.split('\n'):
			# Ignore empty lines
			if not l.strip():
				continue

			arr = l.split(' ')

			# ignore the "whole" disk device (we are interested
			# only in partitions)
			diskname = arr[0]
			if diskname == disk:
				continue

			try:
				size = int(int(arr[1]) / (1024 * 1024))
			except TypeError or ValueError:
				size = 0

			uuid = arr[2]
			label = arr[3]
			mountpoint = arr[4]
			fstype = arr[5]

			if not mountpoint:
				mountpoint = get_host_mount_point(host_fstab, uuid, label)

			partnumber = get_disk_part_number(diskname)

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


def get_host_fstab(disks):
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
		for d in get_host_partition_devices(disk):
			os.system('mount /dev/%s %s' % (d, mountpoint) + ' > /dev/null 2>&1')

			if os.path.exists(fstab):
				with open(fstab) as file:
					for line in file.readlines():
						entry = {}
						# Yank out any comments in fstab:
						if '#' in line:
							line = line.split('#')[0]
						split_line = line.split()
						if len(split_line) < 3:
							continue

						entry['device'] = split_line[0].strip()
						entry['mountpoint'] = split_line[1].strip()
						entry['fstype'] = split_line[2].strip()

						host_fstab.append(entry)
					# We may need the fstab file for post-install
				if not os.path.exists(fs_info):
					os.makedirs(fs_info)
				copy(fstab, fs_info)
			os.system('umount %s 2> /dev/null' % mountpoint)

			if host_fstab:
				break
		if host_fstab:
			break

	try:
		os.removedirs(mountpoint)
	except:
		pass

	return host_fstab


def prettify(element):
	"""Return a pretty-printed XML string for the Element."""
	rough_string = ElementTree.tostring(element, 'utf-8')
	reparsed = xml.dom.minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="\t")

def main():
	"""Where the magic begins."""
	global host_partitions
	global csv_partitions
	host_disks = get_host_disks()

	count = 5
	while count > 0:
		if len(host_disks) == 0:
			time.sleep(1)
			count -= 1
			host_disks = get_host_disks()
		else:
			break

	host_fstab = get_host_fstab(host_disks)
	host_partitions = get_host_partitions(host_disks, host_fstab)

	if not csv_partitions:
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

	#
	# there are 2 scenarios:
	#
	# 1) nukedisks == True
	# 2) nukedisks == False
	# 3) nukedisks == a list of disks to nuke <-- Not sure we actually handle this yet.
	#
	# 1 is easy -- nuke the disks and recreate the partitions specified in the
	# "partitions" variable
	#
	# For 2, reformat "/", "/boot" (if present) and "/var" on the boot disk, then
	# reconnect all other discovered partitions.

	# if host_fstab is an empty list, turning on nukedisks=True" to avoid SLES defaults
	if host_fstab == []:
		nuke_disks = True
		attributes['nukedisks'] = "True"
	elif 'nukedisks' in attributes:
		nuke_disks = str2bool(attributes['nukedisks'])
	else:
		nuke_disks = False
		attributes['nukedisks'] = "False"

	if not nuke_disks:
		# Need output of the existing fstab to be utilized for post-install script.
		if not os.path.exists(fs_info):
			os.makedirs(fs_info)
		with open(str(fs_info + '/__init__.py'), 'w') as fstab_info:
			fstab_info.write('old_fstab = %s\n\n' % host_fstab)

	#
	# process all nuked disks first
	#
	nuke_list = get_nukes(host_disks, nuke_disks, attributes['nukedisks'])

	for disk in nuke_list:
		nuke_it(disk)

		initialize = True
		output_disk(disk, initialize)
	#
	# now process all non-nuked disks
	#
	initialize = False
	for disk in host_disks:
		if disk not in nuke_list:
			output_disk(disk, initialize)

	print(prettify(partitioning_config))


if __name__ == "__main__":
	main()