import paramiko
import math

def get_partitions(testinfra_host):

	# For a given testinfra host, return a list of all partitions across disks
	try:
		return testinfra_host.check_output(f'lsblk -r -n -o name').split('\n')

	# If we can't ssh, return a blank list
	except paramiko.ssh_exception.NoValidConnectionsError:
		return []

def get_part_label(testinfra_host, partition):

	# For a given partition and testinfra host, return the partition label
	# if it is has one, otherwise return 'no label'
	try:
		labels = testinfra_host.check_output(f'lsblk -r -n -o name,label').split('\n')

	# If we can't ssh, return 'no label'
	except paramiko.ssh_exception.NoValidConnectionsError:
		return None

	# Try all labels on the host
	for label in labels:
		try:
			curr_part = label.split(' ')[0]
			curr_label = label.split(' ')[1]

		except IndexError:
			return None

		# If the partition matches the argument one, return the label
		if curr_part == partition:
			return curr_label

	# Otherwise return no label
	return None

def get_part_mountpoint(testinfra_host, partition):

	# For a given partition and testinfra host, return the partition mountpoint
	# if it is has one, otherwise return 'no mountpoint'
	try:
		mounts = testinfra_host.check_output(f'lsblk -r -n -o name,mountpoint').split('\n')

	# If we can't ssh, return there is no mountpoint
	except paramiko.ssh_exception.NoValidConnectionsError:
		return None

	# Try all mountpoints on the host
	for mount in mounts:
		try:
			curr_part = mount.split(' ')[0]
			curr_mount = mount.split(' ')[1]

		except IndexError:
			return None

		# If the partition matches the argument one, return the mountpoint
		if curr_part == partition:
			return curr_mount

	# Otherwise return no mountpoint
	return None

def get_part_fs(testinfra_host, partition):

	# For a testinfra host and partition, return the partition
	# filesystem
	try:
		fstypes = testinfra_host.check_output(f'lsblk -r -n -o name,fstype').split('\n')

	# Return blank if we can't ssh into the host
	except paramiko.ssh_exception.NoValidConnectionsError:
		return ''

	# Go through all found partitions on the host
	for fs in fstypes:
		try:
			curr_part = fs.split(' ')[0]
			curr_fs = fs.split(' ')[1]

		except IndexError:
			return None

		# If the current partition matches the the input one
		# return the file system
		if curr_part == partition:
			return curr_fs

	# Otherwise return blank
	return None

def get_part_size(testinfra_host, partition):

	# For a testinfra host and partition, return the partition's
	# size if it can be found
	try:
		sizes = testinfra_host.check_output(f'lsblk -b -r -n -o name,size').split('\n')

	# If we can't ssh into the host, return an invalid size
	except paramiko.ssh_exception.NoValidConnectionsError:
		return -1

	# Go through all the partitions
	for size in sizes:
		try:
			curr_part = size.split(' ')[0]
			curr_size = size.split(' ')[1]

		except IndexError:
			return None

		# If the current partition matches the input one
		# return the partition size in megabytes since
		# lsblk can only do bytes precisely
		if curr_part == partition:
			return int(curr_size) / math.pow(2,20)

	# Otherwise return an invalid size
	return None
