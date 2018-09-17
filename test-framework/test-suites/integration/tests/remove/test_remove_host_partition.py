import json
from textwrap import dedent


class TestRemoveHostPartition:
	def test_remove_host_partition_no_hosts(self, host):
		result = host.run('stack remove host partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [device=string] [partition=string] [uuid=string]
		''')

	def test_remove_host_partition_no_matching_hosts(self, host):
		result = host.run('stack remove host partition a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [device=string] [partition=string] [uuid=string]
		''')

	def test_remove_host_partition_no_parameters(self, host, add_host):
		# Add the same partition info to both hosts
		result = host.run('stack add host partition frontend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
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

		# Now remove just the backend's info
		result = host.run('stack remove host partition backend-0-0')
		assert result.rc == 0

		# Confirm it got deleted
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
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

	def test_remove_host_partition_with_uuid(self, host, add_host):
		# Add the same partition info to both hosts
		result = host.run('stack add host partition frontend-0-0 device=sda1 uuid=test')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda1 uuid=test')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2  uuid=foo')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
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
				'uuid': 'test'
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
				'uuid': 'foo'
			}
		]

		# Now remove just the backend's info for uuid test
		result = host.run('stack remove host partition backend-0-0 uuid=test')
		assert result.rc == 0

		# Confirm it got deleted
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
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
				'uuid': 'foo'
			}
		]

	def test_remove_host_partition_with_parition(self, host, add_host):
		# Add the same partition info to both hosts
		result = host.run('stack add host partition frontend-0-0 device=sda1 mountpoint=/')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda1 mountpoint=/')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2 mountpoint=/var')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '/',
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
				'mountpoint': '/',
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
				'mountpoint': '/var',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			}
		]

		# Now remove just the backend's info for the root partition
		result = host.run('stack remove host partition backend-0-0 partition=/')
		assert result.rc == 0

		# Confirm it got deleted
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '/',
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
				'mountpoint': '/var',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': ''
			}
		]

	def test_remove_host_partition_with_device(self, host, add_host):
		# Add the same partition info to both hosts
		result = host.run('stack add host partition frontend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda1')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
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

		# Now remove just the backend's info for the sda1 device
		result = host.run('stack remove host partition backend-0-0 device=sda1')
		assert result.rc == 0

		# Confirm it got deleted
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
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

	def test_remove_host_partition_with_all_parameters(self, host, add_host):
		# Add the same partition info to both hosts
		result = host.run('stack add host partition frontend-0-0 device=sda1 mountpoint=/ uuid=test')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda1 mountpoint=/ uuid=test')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2 mountpoint=/var uuid=foo')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '/',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
			},
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '/',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '/var',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'foo'
			}
		]

		# Now remove just the backend's info for the sda1 device
		result = host.run('stack remove host partition backend-0-0 device=sda1 partition=/ uuid=test')
		assert result.rc == 0

		# Confirm it got deleted
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '/',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '/var',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'foo'
			}
		]

	def test_remove_host_partition_multiple_hosts(self, host, add_host):
		# Add the same partition info to both hosts
		result = host.run('stack add host partition frontend-0-0 device=sda1 mountpoint=/ uuid=test')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda1 mountpoint=/ uuid=test')
		assert result.rc == 0

		result = host.run('stack add host partition backend-0-0 device=sda2 mountpoint=/var uuid=foo')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'frontend-0-0',
				'id': '',
				'mountpoint': '/',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
			},
			{
				'device': 'sda1',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '/',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'test'
			},
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '/var',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'foo'
			}
		]

		# Now remove both host's info for the sda1 device
		result = host.run('stack remove host partition frontend-0-0 backend-0-0 device=sda1 partition=/ uuid=test')
		assert result.rc == 0

		# Confirm they got deleted
		result = host.run('stack list host partition frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda2',
				'flags': '',
				'formatflags': '',
				'host': 'backend-0-0',
				'id': '',
				'mountpoint': '/var',
				'size': '0',
				'start': '0',
				'type': '',
				'uuid': 'foo'
			}
		]
