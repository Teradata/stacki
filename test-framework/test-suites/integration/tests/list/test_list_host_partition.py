import json


class TestListHostPartition:
	def test_list_host_partition_invalid(self, host):
		result = host.run('stack list host partition test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_list_host_partition_no_args(self, host, add_host):
		# Add some partition info to the frontend
		result = host.run('stack add host partition frontend-0-0 device=sda '
			'mountpoint=/ uuid=test_uuid sectorstart=1234 size=5678 partid=1 '
			'fs=ext4 partitionflags=test_partition formatflags=test_format')
		assert result.rc == 0

		# Add a few partitions to the backend as well
		result = host.run('stack add host partition backend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2')
		assert result.rc == 0

		# Make sure a list shows them
		result = host.run('stack list host partition output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda',
				'flags': 'test_partition',
				'formatflags': 'test_format',
				'host': 'frontend-0-0',
				'id': '1',
				'mountpoint': '/',
				'size': '5678',
				'start': '1234',
				'type': 'ext4',
				'uuid': 'test_uuid'
			},
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			}
		]

	def test_list_host_partition_one_arg(self, host, add_host):
		# Add some partition info to the frontend
		result = host.run('stack add host partition frontend-0-0 device=sda1 '
			'mountpoint=/ uuid=test_uuid sectorstart=1234 size=5678 partid=1 '
			'fs=ext4 partitionflags=test_partition formatflags=test_format')
		assert result.rc == 0

		result = host.run('stack add host partition frontend-0-0 device=sda2')
		assert result.rc == 0

		# Add a few partitions to the backend as well, which should be skipped
		result = host.run('stack add host partition backend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2')
		assert result.rc == 0

		# Make sure only the frontend partitions are listed
		result = host.run('stack list host partition frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': 'test_partition',
				'formatflags': 'test_format',
				'host': 'frontend-0-0',
				'id': '1',
				'mountpoint': '/',
				'size': '5678',
				'start': '1234',
				'type': 'ext4',
				'uuid': 'test_uuid'
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			}
		]

	def test_list_host_partition_multiple_args(self, host, add_host):
		# Add some partition info to the frontend
		result = host.run('stack add host partition frontend-0-0 device=sda1 '
			'mountpoint=/ uuid=test_uuid sectorstart=1234 size=5678 partid=1 '
			'fs=ext4 partitionflags=test_partition formatflags=test_format')
		assert result.rc == 0

		result = host.run('stack add host partition frontend-0-0 device=sda2')
		assert result.rc == 0

		# Add a few partitions to the backend as well
		result = host.run('stack add host partition backend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2')
		assert result.rc == 0

		# Add another backend so we can make sure it is skipped in the listing
		add_host('backend-0-1', '0', '2', 'backend')

		# Add a few partitions to the second backend
		result = host.run('stack add host partition backend-0-1 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-1 device=sda2')
		assert result.rc == 0

		# Now, make sure only the frontend and backend-0-0 partitions are listed
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': 'test_partition',
				'formatflags': 'test_format',
				'host': 'frontend-0-0',
				'id': '1',
				'mountpoint': '/',
				'size': '5678',
				'start': '1234',
				'type': 'ext4',
				'uuid': 'test_uuid'
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			},
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			}
		]
