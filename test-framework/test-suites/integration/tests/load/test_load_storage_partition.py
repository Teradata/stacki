import json
from textwrap import dedent


class TestLoadStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack load storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "file" parameter is required
			{file=string} [processor=string]
		''')

	def test_missing_file(self, host):
		result = host.run('stack load storage partition file=/tmp/foo')
		assert result.rc == 255
		assert result.stderr == 'error - file "/tmp/foo" does not exist\n'

	def test_missing_headers(self, host, test_file):
		path = test_file('load/storage_partition_missing_headers.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == (
			'error - the following required fields are not present in the input file: '
			'device, name, size\n'
		)

	def test_missing_size(self, host, test_file):
		path = test_file('load/storage_partition_missing_size.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - empty value found for "size" column at line 2\n'

	def test_invalid_size(self, host, test_file):
		path = test_file('load/storage_partition_invalid_size.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - size "test" must be an integer\n'

	def test_negative_size(self, host, test_file):
		path = test_file('load/storage_partition_negative_size.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - size "-1" must be >= 0\n'

	def test_invalid_partid(self, host, test_file):
		path = test_file('load/storage_partition_invalid_partid.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - partid "test" must be an integer\n'

	def test_negative_partid(self, host, test_file):
		path = test_file('load/storage_partition_negative_partid.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - partid "-1" must be >= 0\n'

	def test_missing_name(self, host, test_file):
		path = test_file('load/storage_partition_missing_name.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - empty host name found in "name" column\n'

	def test_invalid_name(self, host, test_file):
		path = test_file('load/storage_partition_invalid_name.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - Cannot find host "a:backend"\n'

	def test_missing_device(self, host, test_file):
		path = test_file('load/storage_partition_missing_device.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - empty value found for "device" column at line 2\n'

	def test_swap_hibernation_size(self, host, test_file):
		path = test_file('load/storage_partition_swap_hibernation_size.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run('stack list storage partition output-format=json')

		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"device": "sda",
				"partid": 1,
				"mountpoint": "swap",
				"size": "hibernation",
				"fstype": "swap",
				"options": ""
			},
			{
				"device": "sda",
				"partid": 2,
				"mountpoint": "/",
				"size": 0,
				"fstype": "xfs",
				"options": ""
			}
		]

	def test_swap_recommended_size(self, host, test_file):
		path = test_file('load/storage_partition_swap_recommended_size.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run('stack list storage partition output-format=json')

		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"device": "sda",
				"partid": 1,
				"mountpoint": "swap",
				"size": "recommended",
				"fstype": "swap",
				"options": ""
			},
			{
				"device": "sda",
				"partid": 2,
				"mountpoint": "/",
				"size": 0,
				"fstype": "xfs",
				"options": ""
			}
		]

	def test_global_scope(self, host, test_file):
		path = test_file('load/storage_partition_global_scope.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run('stack list storage partition output-format=json')

		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"device": "sda",
				"partid": 1,
				"mountpoint": None,
				"size": 40,
				"fstype": None,
				"options": "--asprimary --partition_id=18"
			},
			{
				"device": "sda",
				"partid": 2,
				"mountpoint": "/",
				"size": 30720,
				"fstype": "ext4",
				"options": "--asprimary --label=ROOT-BE1"
			},
			{
				"device": "sda",
				"partid": 3,
				"mountpoint": None,
				"size": 30720,
				"fstype": "ext4",
				"options": "--asprimary --label=ROOT-BE2"
			}
		]

	def test_appliance_scope(self, host, test_file):
		path = test_file('load/storage_partition_appliance_scope.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run(
			'stack list appliance storage partition backend output-format=json'
		)
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "backend",
				"device": "sda",
				"partid": 1,
				"mountpoint": "/",
				"size": 0,
				"fstype": "ext4",
				"options": ""
			},
			{
				"appliance": "backend",
				"device": "sdb",
				"partid": 2,
				"mountpoint": "/home",
				"size": 0,
				"fstype": "ext4",
				"options": "--label=HOME"
			}
		]

	def test_os_scope(self, host, test_file):
		path = test_file('load/storage_partition_os_scope.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run(
			'stack list os storage partition sles output-format=json'
		)

		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"os": "sles",
				"device": "sda",
				"partid": 1,
				"mountpoint": "/",
				"size": 0,
				"fstype": "ext4",
				"options": ""
			},
			{
				"os": "sles",
				"device": "sdb",
				"partid": 2,
				"mountpoint": "/home",
				"size": 0,
				"fstype": "ext4",
				"options": "--label=HOME"
			}
		]

	def test_host_scope(self, host, add_host, test_file):
		path = test_file('load/storage_partition_host_scope.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run(
			'stack list host storage partition backend-0-0 output-format=json'
		)
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"host": "backend-0-0",
			"device": "sda",
			"partid": 1,
			"mountpoint": "/",
			"size": 0,
			"fstype": "ext4",
			"options": "",
			"source": "H"
		}]

	def test_raid_and_lvm(self, host, test_file):
		path = test_file('load/storage_partition_raid_and_lvm.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		result = host.run('stack list storage partition output-format=json')

		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"device": "md0",
				"partid": 1,
				"mountpoint": "/",
				"size": 0,
				"fstype": "ext4",
				"options": "--level=RAID1 raid.01 raid.02"
			},
			{
				"device": "md1",
				"partid": 2,
				"mountpoint": "pv.01",
				"size": 0,
				"fstype": "lvm",
				"options": "--level=RAID0 raid.03 raid.04"
			},
			{
				"device": "pv.01",
				"partid": 7,
				"mountpoint": "volgrp01",
				"size": 0,
				"fstype": "volgroup",
				"options": ""
			},
			{
				"device": "sda",
				"partid": 3,
				"mountpoint": "raid.01",
				"size": 16000,
				"fstype": "raid",
				"options": ""
			},
			{
				"device": "sda",
				"partid": 5,
				"mountpoint": "raid.03",
				"size": 16000,
				"fstype": "raid",
				"options": ""
			},
			{
				"device": "sdb",
				"partid": 4,
				"mountpoint": "raid.02",
				"size": 16000,
				"fstype": "raid",
				"options": ""
			},
			{
				"device": "sdb",
				"partid": 6,
				"mountpoint": "raid.04",
				"size": 16000,
				"fstype": "raid",
				"options": ""
			},
			{
				"device": "volgrp01",
				"partid": 8,
				"mountpoint": "/var",
				"size": 0,
				"fstype": "xfs",
				"options": "--name=var"
			}
		]

	def test_raid_missing_options(self, host, test_file):
		path = test_file('load/storage_partition_raid_missing_options.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - missing options for software raid device "md0"\n'

	def test_raid_missing_level(self, host, test_file):
		path = test_file('load/storage_partition_raid_missing_level.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - missing "--level=RAID" option for software raid device "md0"\n'

	def test_raid_missing_device(self, host, test_file):
		path = test_file('load/storage_partition_raid_missing_device.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - device "raid.02" not defined for software raid device "md0"\n'

	def test_lvm_missing_name(self, host, test_file):
		path = test_file('load/storage_partition_lvm_missing_name.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - missing "--name" option for LVM partition "/"\n'

	def test_lvm_invalid_device(self, host, test_file):
		path = test_file('load/storage_partition_lvm_invalid_device.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - device "pv.02" not defined for volgroup "volgrp01"\n'

	def test_lvm_unknown_device(self, host, test_file):
		path = test_file('load/storage_partition_lvm_unknown_device.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - unknown device(s) detected: volgrp02\n'

	def test_create_spreadsheet_dirs(self, host, test_file, rmtree):
		# Remove the existing spreadsheets directory
		rmtree('/export/stack/spreadsheets')

		# Confirm the tree is gone
		assert not host.file('/export/stack/spreadsheets').exists

		# Load a spreadsheet, to cause the directories to get created
		path = test_file('load/storage_partition_global_scope.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 0

		# Make sure they are there now
		assert host.file('/export/stack/spreadsheets').exists
		assert host.file('/export/stack/spreadsheets/RCS').exists

	def test_unicode_decode_error(self, host, test_file):
		path = test_file('load/storage_partition_unicode_decode_error.csv')
		result = host.run(f'stack load storage partition file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - non-ascii character in file\n'
