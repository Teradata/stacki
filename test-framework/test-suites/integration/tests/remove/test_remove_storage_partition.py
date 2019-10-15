import json
from textwrap import dedent


class TestRemoveStoragePartition:
	def test_no_args(self, host):
		result = host.run('stack remove storage partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "device" or "mountpoint" parameter is required
			[device=string] [mountpoint=string]
		''')

	def test_no_matches_on_device(self, host):
		result = host.run('stack remove storage partition device=sda')
		assert result.rc == 255
		assert result.stderr == 'error - partition specification for device "sda" and mount point "*" doesn\'t exist\n'

	def test_no_matches_on_mountpoint(self, host):
		result = host.run('stack remove storage partition mountpoint=/')
		assert result.rc == 255
		assert result.stderr == 'error - partition specification for device "*" and mount point "/" doesn\'t exist\n'

	def test_remove_single_partition(self, host):
		# Add a couple global partitions
		result = host.run(
			'stack add storage partition device=sda mountpoint=/ '
			'size=1024 type=ext4 options=sda_options partid=1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add storage partition device=sdb mountpoint=/var '
			'size=2048 type=ext3 options=sdb_options partid=2'
		)
		assert result.rc == 0

		# Make sure they got added
		result = host.run('stack list storage partition output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda',
				'fstype': 'ext4',
				'mountpoint': '/',
				'options': 'sda_options',
				'partid': 1,
				'size': 1024
			},
			{
				'device': 'sdb',
				'fstype': 'ext3',
				'mountpoint': '/var',
				'options': 'sdb_options',
				'partid': 2,
				'size': 2048
			}
		]

		# Now remove just the sdb partition
		result = host.run('stack remove storage partition mountpoint=/var')
		assert result.rc == 0

		# Make sure only sdb got removed
		result = host.run('stack list storage partition output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'device': 'sda',
			'fstype': 'ext4',
			'mountpoint': '/',
			'options': 'sda_options',
			'partid': 1,
			'size': 1024
		}]

	def test_remove_everything(self, host):
		# Add a couple global partitions
		result = host.run(
			'stack add storage partition device=sda mountpoint=/ '
			'size=1024 type=ext4 options=root_options partid=1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add storage partition device=sda mountpoint=/var '
			'size=2048 type=ext3 options=var_options partid=2'
		)
		assert result.rc == 0

		# Make sure they got added
		result = host.run('stack list storage partition output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda',
				'fstype': 'ext4',
				'mountpoint': '/',
				'options': 'root_options',
				'partid': 1,
				'size': 1024
			},
			{
				'device': 'sda',
				'fstype': 'ext3',
				'mountpoint': '/var',
				'options': 'var_options',
				'partid': 2,
				'size': 2048
			}
		]

		# Now remove everything by specifying the sda device
		result = host.run('stack remove storage partition device=sda')
		assert result.rc == 0

		# Make sure it's all gone
		result = host.run('stack list storage partition')
		assert result.rc == 0
		assert result.stdout == ''
