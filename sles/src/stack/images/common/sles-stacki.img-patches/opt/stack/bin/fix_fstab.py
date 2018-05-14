#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
"""
Called after autoyast does RPM installs.
Fixes the autoyast partitioning if nukedisks=False
Replaces UUID with LABEL then saves variable 'partitions_to_label' for fix_partition to use later
Merges the old fstab that contains unformatted existing partitions with the new fstab from yast.
Called Python with -E, as that's super subtle
"""
import sys
import subprocess
import os
import fileinput
import re
import shutil
try:
	sys.path.append('/tmp')
	from fstab_info import old_fstab
except ModuleNotFoundError:
	# If the file isn't there to import then we didn't do a nukedisks=false with labels
	sys.exit(0)
except ImportError:
	sys.exit(0)

old_fstab_file = '/tmp/fstab_info/fstab'
new_fstab_file = '/mnt/etc/fstab'
tmp_fstab_file = '/tmp/fstab_info/tmp_fstab'


def get_host_partition_devices(detected_disks):
	"""
	Returns the device names of all the partitions on a specific disk
	"""

	devices = []
	p = subprocess.Popen(
			['lsblk', '-nrio', 'NAME', '/dev/%s' % detected_disks],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
	o = p.communicate()[0]
	out = o.decode()

	for l in out.split('\n'):
		# Ignore empty lines
		if not l.strip():
			continue

		# Skip read-only and removable devices
		arr = l.split()
		diskname = arr[0].strip()

		if diskname != detected_disks:
			devices.append(diskname)

	return devices


def get_host_fstab():
	"""Get contents of /etc/fstab by mounting all disks
	and checking if /etc/fstab exists.
	"""
	host_fstab = []
	if os.path.exists(new_fstab_file):
		with open(new_fstab_file) as file:
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

	return host_fstab


def get_existing_labels(yast_fstab, existing_fstab):
	"""Compare the two fstab inputs to determine which didn't have their LABEL= applied from autoyast.
	Returns a new list of dictionaries that contains the new identifier and the fstype"""
	no_labels = []
	existing_labels = []
	new_data = {}

	for mount in yast_fstab:
		if 'label' not in mount['device'].lower():
			# Create list to check against old_fstab
			no_labels.append(mount['mountpoint'])
			# Capture new data based on mountpoint key
			new_data[mount['mountpoint']] = [mount['device'], mount['fstype']]

	for mount in existing_fstab:
		if 'label' in mount['device'].lower() and mount['mountpoint'] in no_labels:
			if mount['fstype'] != new_data[mount['mountpoint']][1]:
				print("fstype changed during reinstall!")
			else:
				mount['new_uuid'] = new_data[mount['mountpoint']][0]
				mount['new_fstype'] = new_data[mount['mountpoint']][1]
				existing_labels.append(mount)

	return existing_labels


def edit_new_fstab(partitions_to_label):
	"""Edit the /mnt/etc/fstab to replace the UUID= with LABEL=."""
	for partition in partitions_to_label:
		if len(partition) == 5:
			find = partition['new_uuid']
			replace = partition['device']
			with fileinput.FileInput(new_fstab_file, inplace=True) as fstab:
				for line in fstab:
					if find in line:
						print(line.replace(find, replace), end='')
					# leave the line alone
					else:
						print(line, end='')


def edit_old_fstab(yast_fstab, existing_fstab):
	"""Remove any partitions from the existing fstab if they exist in the yast generated fstab.
	We determine that they already exist by keying off the mount point."""
	new_mount_points = []
	for entry in yast_fstab:
		new_mount_points.append(entry['mountpoint'])
	for entry in existing_fstab:
		if entry['mountpoint'] in new_mount_points:
			remove = r'^' + re.escape(entry['device']) + r'.*' + re.escape(entry['mountpoint']) + r'.*'
			# remove = r'^' + entry['device'] + '.*' + entry['mountpoint'] + '.*'
			with fileinput.FileInput(old_fstab_file, inplace=True) as fstab:
				for line in fstab:
					if not re.search(remove, line):
						print(line, end='')


def merge_fstabs():
	"""After editing the old and new fstab, merge them together to contain all needed data."""
	with open(tmp_fstab_file, 'w+b') as new_file:
		for each_file in [new_fstab_file, old_fstab_file]:
			with open(each_file, 'rb') as old_file:
				shutil.copyfileobj(old_file, new_file)

def main():
	"""Main function."""
	new_fstab = get_host_fstab()
	partitions_to_label = get_existing_labels(new_fstab, old_fstab)
	edit_old_fstab(new_fstab, old_fstab)
	edit_new_fstab(partitions_to_label)
	merge_fstabs()
	shutil.copy(tmp_fstab_file, new_fstab_file)
	# Need output of the partitions_to_label to be utilized for post autoyast script.
	if not os.path.exists('/tmp/fstab_info'):
		os.makedirs('/tmp/fstab_info')
	with open('/tmp/fstab_info/__init__.py', 'a') as fstab_info:
		fstab_info.write('partitions_to_label = %s\n\n' % partitions_to_label)

if __name__ == "__main__":
	main()