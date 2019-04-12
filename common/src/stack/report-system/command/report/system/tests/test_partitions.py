import pytest
import math
import json
import testinfra
import paramiko
from collections import namedtuple, defaultdict
from stack import api
from stack.commands.report.system.tests.stack_test_util import get_partitions, get_part_label, get_part_size, get_part_fs

testinfra_hosts = list(set([host['host'] for host in api.Call('list host partition')]))
class TestStoragePartition:

	""" Test if the way stacki configured the disks is still how they are partitioned """

	def test_storage_partition(self, host):

		# Get current hostname and test if we can ssh into the host
		# Otherwise fail the test
		try:
			hostname = host.check_output('hostname')

		except paramiko.ssh_exception.NoValidConnectionsError:
			pytest.fail(f'Could not ssh into host')

		# Get stacki storage config using proper scoping
		storage_config = api.Call(f'list host storage partition {hostname}')
		check_config = defaultdict(dict)
		partition_info = namedtuple('partition', ['name', 'mountpoint', 'label', 'fstype', 'size'])
		errors = []

		# Otherwise if we are on an older version of stacki without proper scoping,
		# use report host instead and convert the dict output as a string into an actual dict
		if not storage_config:
			report_storage = api.Call(f'report host storage partition {hostname}')

			# If we still cannot get stacki's storage config for the current host,
			# skip the test
			if not report_storage or report_storage[0] == '[]':
				pytest.skip(f'Using default stacki partition config for host {hostname}')
			else:
				storage_config = json.loads(report_storage[0].replace("'", '"').replace('None', '""'))

		# Get a list of the partitions that are actually on the disk
		host_partitions = get_partitions(host)

		if not host_partitions:
			pytest.fail(f'No partitions found on host {hostname}')

		# Go through the stacki storage config and see
		# if it matches what's actually on the disk/disks
		for partition in storage_config:
			# Info needed for each partiton
			disk = partition['device']
			disk_num = str(partition['partid'])
			partition_name = disk + disk_num
			partition_size = get_part_size(host, partition_name)
			conf_mntpt = partition['mountpoint']
			part_label = ''

			# If a partition cannot be found on the actual disk, return an error
			if partition_name not in host_partitions:
				errors.append(f'/dev/{partition_name} not found on host')
				continue

			# Because testinfra only has mountpoint based partition functions
			# use them when we can but if there is a partition without a mountpoint
			# check using a fixture that directly calls lsblk
			if conf_mntpt:

				if not host.mount_point(conf_mntpt).exists:
					errors.append(f'Could not find {conf_mntpt} on disk')

				else:
					curr_mnt_part = host.mount_point(conf_mntpt).device
					curr_fs = host.mount_point(conf_mntpt).filesystem

					if curr_mnt_part != f'/dev/{partition_name}':
						msg = f'Mountpoint {conf_mntpt} found at {curr_mnt_part} but was configured to be at /dev/{partition_name}'
						errors.append(msg)

					if (curr_fs != partition['fstype']) and partition['fstype']:
						errors.append(
							f'/dev/{partition_name} found with file system {curr_fs} but was configured with {partition["fstype"]}'
						)

			else:

				# Use fixture instead of testinfra since there isn't a mountpoint
				curr_fs = get_part_fs(host, partition_name)
				if curr_fs != partition['fstype'] and (partition['fstype'] != None):
					errors.append(
						f'/dev/{partition_name} found with file system {curr_fs} but was configured with {partition["fstype"]}'
					)

			# Check if the a label should be present for the current partition
			# and check if it matches the actual partition
			if 'label=' in partition['options']:
				config_label = partition['options'].split('label=')[1]
				curr_label = get_part_label(host, partition_name)

				if not curr_label:
					errors.append(f'/dev/{partition_name} configured with label {config_label} but no label found')

				elif config_label != curr_label:
					errors.append(f'/dev/{partition_name} configured with label {config_label} but found with {curr_label}')

			# Check partition size within 100MB due to lsblk bytes conversion
			# If a partition size is 0, we assume that means it fills the rest of the disk
			# So check that as well
			if not math.isclose(int(partition['size']), partition_size, abs_tol=100):

				# Initial check will not match if partition size as 0, as it fills the rest
				# of the disk
				if int(partition['size']) == 0:
					disk_size = get_part_size(host, disk)
					rest_of_disk = 0

					# Find the size of the disk for all the other partitions
					for partition in storage_config:
						curr_partition = partition['device'] + str(partition['partid'])

						# Don't include the current partition
						if curr_partition != partition_name:
							part_size = get_part_size(host, curr_partition)
							if part_size:
								rest_of_disk += part_size

					# Check if the disk size matches all the partitions added up
					if not math.isclose(partition_size+rest_of_disk, disk_size, abs_tol=100):
						errors.append(f'/dev/{partition_name} size different from configuration')
				else:
					errors.append(f'/dev/{partition_name} size different from configuration')

		assert not errors, f'Host {hostname} found with partitioning mismatch from original config: {", ".join(errors)}'
