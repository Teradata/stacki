import json
from textwrap import dedent


class TestAddHostPartition:
	def test_add_host_partition_no_hosts(self, host):
		result = host.run('stack add host partition')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [device=string] [formatflags=string] [fs=string] [mountpoint=string] [partid=string] [partitionflags=string] [sectorstart=string] [size=string] [uuid=string]
		''')
	
	def test_add_host_partition_no_matching_hosts(self, host):
		result = host.run('stack add host partition a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [device=string] [formatflags=string] [fs=string] [mountpoint=string] [partid=string] [partitionflags=string] [sectorstart=string] [size=string] [uuid=string]
		''')
	
	def test_add_host_partition_no_device(self, host):
		result = host.run('stack add host partition frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "device" parameter is required
			{host ...} [device=string] [formatflags=string] [fs=string] [mountpoint=string] [partid=string] [partitionflags=string] [sectorstart=string] [size=string] [uuid=string]
		''')
	
	def test_add_host_partition_no_existing_info(self, host, add_host):
		# Add the partition info
		result = host.run('stack add host partition backend-0-0 device=sda')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda',
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
	
	def test_add_host_partition_with_existing_info(self, host, add_host):
		# Add some existing partition info
		result = host.run('stack add host partition backend-0-0 device=sda mountpoint=/delete_me')
		assert result.rc == 0
		
		result = host.run('stack add host partition backend-0-0 device=sda mountpoint=/delete_me_too')
		assert result.rc == 0
		
		# Now add our new partition info
		result = host.run('stack add host partition backend-0-0 device=sda')
		assert result.rc == 0

		# Check that it made it into the database and replaced the old stuff
		result = host.run('stack list host partition backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda',
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
	
	def test_add_host_partition_all_parameters(self, host, add_host):
		# Add the partition info
		result = host.run('stack add host partition backend-0-0 device=sda '
			'mountpoint=/ uuid=test_uuid sectorstart=1234 size=5678 partid=1 '
			'fs=ext4 partitionflags=test_partition formatflags=test_format')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host partition backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'device': 'sda',
				'flags': 'test_partition',
				'formatflags': 'test_format',
				'host': 'backend-0-0',
				'id': '1',
				'mountpoint': '/',
				'size': '5678',
				'start': '1234',
				'type': 'ext4',
				'uuid': 'test_uuid'
			}
		]
