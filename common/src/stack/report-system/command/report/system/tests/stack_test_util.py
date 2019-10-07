import paramiko
import math

def get_partitions(testinfra_host):

	# For a given testinfra host, return a list of all partitions across disks
	try:
		return testinfra_host.check_output(
			'lsblk --raw --noheadings --output name'
		).splitlines()

	# If we can't ssh, return a blank list
	except paramiko.ssh_exception.NoValidConnectionsError:
		return []

def get_part_label(testinfra_host, match_key):
	"""Get the partition label based on mountpoint or partition name.

	Returns None if no maching partition can be found.
	"""
	# For a given partition and testinfra host, return the partition label
	try:
		lines = testinfra_host.check_output(
			'lsblk --raw --noheadings --output name,mountpoint,label'
		).splitlines()

	# If we can't ssh, return 'no label'
	except paramiko.ssh_exception.NoValidConnectionsError:
		return None

	# Try all labels on the host
	for line in lines:
		try:
			# lsblk adds an extra space in between when a column is
			# empty, so we explicitly split on a space so that the
			# empty column comes out as an empty string in the list.
			# I.E. 'sda  foolabel'.split(' ') becomes ['sda', '', 'foolabel']
			curr_part, curr_mountpoint, curr_label = line.split(' ')

		# Error when there are not enough values to unpack.
		except ValueError:
			continue

		# If the partition matches the argument one, return the label
		if match_key in (curr_part, curr_mountpoint):
			return curr_label

	# Otherwise return no label
	return None

def get_part_mountpoint(testinfra_host, partition):

	# For a given partition and testinfra host, return the partition mountpoint
	# if it is has one, otherwise return 'no mountpoint'
	try:
		mounts = testinfra_host.check_output(
			'lsblk --raw --noheadings --output name,mountpoint'
		).splitlines()

	# If we can't ssh, return there is no mountpoint
	except paramiko.ssh_exception.NoValidConnectionsError:
		return None

	# Try all mountpoints on the host
	for mount in mounts:
		try:
			curr_part, curr_mount = mount.split(' ')

		# Error when there are not enough values to unpack.
		except ValueError:
			continue

		# If the partition matches the argument one, return the mountpoint
		if curr_part == partition:
			return curr_mount

	# Otherwise return no mountpoint
	return None

def get_part_fs(testinfra_host, partition):
	# For a testinfra host and partition, return the partition
	# filesystem
	try:
		fstypes = testinfra_host.check_output(
			'lsblk --raw --noheadings --output name,fstype'
		).splitlines()

	# Return blank if we can't ssh into the host
	except paramiko.ssh_exception.NoValidConnectionsError:
		return None

	# Go through all found partitions on the host
	for fs in fstypes:
		try:
			curr_part, curr_fs = fs.split(' ')

		# Error when there are not enough values to unpack.
		except ValueError:
			continue

		# If the current partition matches the the input one
		# return the file system
		if curr_part == partition:
			return curr_fs

	# Otherwise return blank
	return None

def get_part_size(testinfra_host, match_key):
	"""Get the partition size based on mountpoint or partition name.

	Returns -1 if no maching partition can be found.
	"""
	# For a testinfra host and partition, return the partition's
	# size if it can be found
	try:
		lines = testinfra_host.check_output(
			'lsblk --bytes --raw --noheadings --output name,mountpoint,size'
		).splitlines()

	# If we can't ssh into the host, return an invalid size
	except paramiko.ssh_exception.NoValidConnectionsError:
		return -1

	# Go through all the partitions
	for line in lines:
		try:
			# lsblk adds an extra space in between when a column is
			# empty, so we explicitly split on a space so that the
			# empty column comes out as an empty string in the list.
			# I.E. 'sda  536870912000'.split(' ') becomes ['sda', '', '536870912000']
			curr_part, curr_mountpount, curr_size = line.split(' ')

		# Error when there are not enough values to unpack.
		except ValueError:
			continue

		# If the current partition matches the input one
		# return the partition size in megabytes since
		# lsblk can only do bytes precisely
		if match_key in (curr_part, curr_mountpount):
			return int(curr_size) / math.pow(2,20)

	# Otherwise return an invalid size
	return -1
