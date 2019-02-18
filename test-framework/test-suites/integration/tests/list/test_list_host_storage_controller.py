import json


class TestListHostStorageController:
	def test_scope_resolving(self, host, add_host_with_interface, add_environment, host_os, test_file):
		# Add our host to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Add a bunch of controller entries that will be overridden to just one entry
		result = host.run(
			'stack add storage controller raidlevel=0 enclosure=1 '
			'adapter=2 arrayid=3 slot=4 hotspare=5 options=test_global'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance storage controller backend raidlevel=1 enclosure=2 '
			'adapter=3 arrayid=4 slot=5,6 hotspare=7 options=test_appliance'
		)
		assert result.rc == 0

		result = host.run(
			f'stack add os storage controller {host_os} raidlevel=5 enclosure=3 '
			f'adapter=4 arrayid=5 slot=6,7,8 hotspare=9 options=test_os'
		)
		assert result.rc == 0

		result = host.run(
			'stack add environment storage controller test raidlevel=6 enclosure=4 '
			'adapter=5 arrayid=6 slot=7,8,9,10 hotspare=11 options=test_environment'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host storage controller backend-0-0 raidlevel=10 enclosure=5 '
			'adapter=6 arrayid=7 slot=8,9 hotspare=10 options=test_host'
		)
		assert result.rc == 0

		# Now list all the host controller entries and see if they match what we expect
		result = host.run('stack list host storage controller backend-0-0 output-format=json')
		assert result.rc == 0

		with open(test_file('list/host_storage_controller_scope_resolving.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_scope_no_enviroment(self, host, add_host, test_file):
		# Create some more hosts
		add_host('backend-0-1', '0', '1', 'backend')
		add_host('backend-0-2', '0', '2', 'backend')

		# Some host storage controller entries for each host
		result = host.run(
			'stack add host storage controller backend-0-0 raidlevel=0 arrayid=1 slot=1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host storage controller backend-0-1 raidlevel=0 arrayid=1 slot=2'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host storage controller backend-0-2 raidlevel=0 arrayid=1 slot=3'
		)
		assert result.rc == 0

		# Now list all the host controller entries and see if they match what we expect
		result = host.run('stack list host storage controller backend-0-0 output-format=json')
		assert result.rc == 0

		with open(test_file('list/host_storage_controller_scope_no_enviroment.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())
