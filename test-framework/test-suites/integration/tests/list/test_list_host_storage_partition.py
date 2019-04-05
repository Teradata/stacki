import json


class TestListHostStoragePartition:
	def test_scope_resolving(self, host, add_host_with_interface, add_environment, host_os, test_file):
		# Add our host to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Add a bunch of partition entries in all the scopes, with unique dummy data.
		result = host.run(
			'stack add storage partition device=disk1 mountpoint=/global '
			'size=1 type=btrfs options=global_options partid=1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance storage partition backend device=disk2 '
			'mountpoint=/app size=2 type=zfs options=app_options partid=2'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os storage partition {host_os} device=disk3 '
			'mountpoint=/os size=3 type=fat16 options=os_options partid=3'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment storage partition test device=disk4 '
			'mountpoint=/env size=4 type=ext3 options=env_options partid=4'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host storage partition backend-0-0 device=sda '
			'mountpoint=/ size=1024 type=ext4 options=host_options partid=5'
		)
		assert result.rc == 0

		# Now list the host partition entries and make sure all the other scopes are overridden
		result = host.run('stack list host storage partition backend-0-0 output-format=json')
		assert result.rc == 0

		with open(test_file('list/host_storage_partition_scope_resolving.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_scope_no_enviroment(self, host, add_host, test_file):
		# Create some more hosts
		add_host('backend-0-1', '0', '1', 'backend')
		add_host('backend-0-2', '0', '2', 'backend')

		# Some host storage controller entries for each host
		result = host.run(
			'stack add host storage partition backend-0-0 device=sda1 size=1024'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host storage partition backend-0-1 device=sda2 size=2048'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host storage partition backend-0-2 device=sda3 size=4096'
		)
		assert result.rc == 0

		# Now list all the host partition entry for the first backend and make sure the
		# data for the other two doesn't sneak in
		result = host.run('stack list host storage partition backend-0-0 output-format=json')
		assert result.rc == 0

		with open(test_file('list/host_storage_partition_scope_no_enviroment.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())
