import pytest
import math
import json
import paramiko
import re
from stack import api
from stack.commands.report.system.tests.stack_test_util import get_part_label, get_part_size

# Test all backend appliances
testinfra_hosts = [host['host'] for host in api.Call('list host a:backend')]

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
		storage_config = api.Call('list host storage partition', [hostname])

		# Otherwise if we are on an older version of stacki without proper scoping,
		# use report host instead and convert the dict output as a string into an actual dict
		if not storage_config:
			report_storage = api.Call('report host storage partition', [hostname])

			# If we still cannot get stacki's storage config for the current host,
			# skip the test
			if not report_storage or report_storage[0] == '[]':
				pytest.skip(f'Using default stacki partition config for host {hostname}')
			else:
				storage_config = json.loads(report_storage[0].replace("'", '"').replace('None', '""'))

		# Go through the stacki storage config and see
		# if it matches what's actually on the disk/disks
		errors = []
		for partition in storage_config:
			# Info needed for each partiton
			conf_mntpt = partition['mountpoint']

			# Check based on mountpoint.
			# TODO: Skip if there is no mountpoint until we better support
			#       OSes that don't preserve partition ordering (like RedHat/CentOS).
			if not conf_mntpt:
				continue

			# TODO: Exclude special swap, biosboot, and LVM partitions for now until
			#       we add support for checking them.
			if any(
				excluded_mountpoint in conf_mntpt.lower()
				for excluded_mountpoint in ("swap", "biosboot", "vg_sys", "pv")
			):
				continue

			# If a mountpoint was configured, it better exist on disk.
			if not host.mount_point(conf_mntpt).exists:
				errors.append(f'Could not find {conf_mntpt} on disk')
				continue

			# Check the FS type if it does exist on disk.
			if host.mount_point(conf_mntpt).filesystem != partition['fstype']:
				errors.append(
					f'{conf_mntpt} found with file system {host.mount_point(conf_mntpt).filesystem} '
					f'but was configured with {partition["fstype"]}'
				)

			# Check partition size within 100MB due to lsblk bytes conversion
			# TODO: If a partition size is 0, skip for now. We can't easily figure out
			#       the expected size of `fill the rest of the disk` partitions due to some
			#       supported OSes not preserving partition ordering, and not all partitions
			#       will have mountpoints.
			expected_size = int(partition['size'])
			actual_size = get_part_size(host, conf_mntpt)
			if expected_size != 0 and not math.isclose(expected_size, actual_size, abs_tol=100):
				errors.append(f'{conf_mntpt} found with size {actual_size} but was configured to be of size {expected_size}')

			# Check if the label should be present for the current partition
			# and check if it matches the actual partition label. The regex captures
			# all non whitespace characters after "--label=" to a named group, and uses
			# that as the label to check against.
			label = re.match(r"^.*--label=(?P<label>\S+)", partition['options'])
			if label and label.groupdict():
				config_label = label.groupdict()['label']
				curr_label = get_part_label(host, conf_mntpt)

				if not curr_label:
					errors.append(f'{conf_mntpt} configured with label {config_label} but no label found')

				elif config_label != curr_label:
					errors.append(f'{conf_mntpt} configured with label {config_label} but found with {curr_label}')

			# Check the options. The regex captures all non whitespace characters after "--fsoptions="
			# to a named group, and uses that as the fsoptions to check against.
			# TODO: We don't currently support the SUSE AutoYaST fsopt key, but this will need to be updated
			#       when we do.
			options = re.match(r"^.*--fsoptions=(?P<options>\S+)", partition["options"])
			if options and options.groupdict():
				# Get a list of options and remove the "defaults" option that doesn't appear to add anything.
				options = [
					option.strip() for option in options.groupdict()["options"].split(",")
					if option.strip() and option != "defaults"
				]
				actual_options = host.mount_point(conf_mntpt).options

				# Since there might be more "default" options than were explicitly specified, just check that
				# each explicitly specified option exists.
				missing_options = [
					option for option in options if option not in actual_options
				]
				if missing_options:
					errors.append(
						f'{conf_mntpt} missing options {missing_options} '
						f'from configured options {actual_options}'
					)

		errors = "\n    ".join(errors)
		assert not errors, f'Host {hostname} found with partitioning mismatch from original config:\n    {errors}'
