#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
"""
Called after autoyast does partition, but before any RPMs are installed to the chroot environment.
Fixes the autoyast partitioning if nukedisks=False
Replaces UUID with LABEL then saves variable 'partitions_to_label' for fix_partition to use later
Called Python with -E, as that's super subtle
"""
import sys
import subprocess
try:
	sys.path.append('/tmp')
	from fstab_info import partitions_to_label
except ModuleNotFoundError:
	# If the file isn't there to import then we didn't do a nukedisks=false with labels
	sys.exit(0)
except ImportError:
	# If the variable isn't there to import then we didn't do a nukedisks=false with labels
	sys.exit(0)


def label_partition(partition):
	"""Determine the filesystem type and take appropriate steps to add a label.
	Assumes the partition being input has the following keys containing data similar to below:
	['device'] = "LABEL=VARBE1"
	['new_uuid'] = "UUID=FFFFFFFFFFFFFFFFFFFF"
	['fstype'] = "ext3"
	['mountpoint'] = "/var"

	Only handles xfs and ext formats.
	The btrfs will remain with it's UUID mount reference
	"""
	return_code = 0
	label = partition['device'].split('=')[1]
	# In sles 11 it uses the /dev/disk/by-id/
	new_id = partition['new_uuid']
	# In sles 12 it uses the uuid=, we need to add the /dev/disk/by-uuid onto the string
	if 'uuid=' in partition['new_uuid'].lower():
		new_id = partition['new_uuid'].split('=')[1]
		new_id = '/dev/disk/by-uuid/%s' % new_id
	if partition['fstype'].lower().startswith('ext'):
		return_code = subprocess.run(['e2label', new_id, '%s' % label]).returncode
	if partition['fstype'].lower().startswith('xfs'):
		# This better be unmount or we will have issues.
		# edit the partition
		return_code = subprocess.run(['xfs_admin', '-L', '%s' % label, new_id]).returncode
	return return_code

def main():
	"""Main function."""
	for each_partition in partitions_to_label:
		# based on the fix_fstab code output, we will only have enough data to safely relabel a partition if
		# we have all 5 variable keys required. ['device'] ['new_uuid'] ['fstype'] ['new_fstype'] ['mountpoint']
		if len(each_partition) == 5:
			label_partition(each_partition)


if __name__ == "__main__":
	main()