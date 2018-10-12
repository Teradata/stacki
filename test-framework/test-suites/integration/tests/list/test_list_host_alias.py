import json
from textwrap import dedent


class TestListHostAlias:
	def test_invalid(self, host, invalid_host):
		result = host.run(f'stack list host alias {invalid_host}')
		assert result.rc == 255
		assert result.stderr == f'error - cannot resolve host "{invalid_host}"\n'

	def test_usage_error(self, host):
		result = host.run('stack list host alias host=frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - Incorrect usage.
			[host ...] [interface=string]
		''')

	def test_no_args(self, host, add_host_with_interface):
		# Add a few aliases
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		result = host.run('stack add host alias backend-0-0 alias=test-1 interface=eth0')
		assert result.rc == 0

		# Make sure a list shows them
		result = host.run('stack list host alias output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'alias': 'test-0',
				'interface': 'eth1'
			},
			{
				'host': 'backend-0-0',
				'alias': 'test-1',
				'interface': 'eth0'
			}
		]

	def test_one_arg(self, host, add_host_with_interface):
		# Add a few aliases for the frontend
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		result = host.run('stack add host alias frontend-0-0 alias=test-1 interface=eth1')
		assert result.rc == 0

		# Add one for the backend so we can make sure the list doesn't include it
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth0')
		assert result.rc == 0

		# Make sure only the frontend aliases are listed
		result = host.run('stack list host alias frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'alias': 'test-0',
				'interface': 'eth1'
			},
			{
				'host': 'frontend-0-0',
				'alias': 'test-1',
				'interface': 'eth1'
			}
		]

	def test_multiple_args(self, host, add_host_with_interface):
		# Add a few aliases for the frontend
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		result = host.run('stack add host alias frontend-0-0 alias=test-1 interface=eth1')
		assert result.rc == 0

		# Add a few for backend-0-0
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth0')
		assert result.rc == 0

		result = host.run('stack add host alias backend-0-0 alias=test-3 interface=eth0')
		assert result.rc == 0

		# Add another backend so we can make sure it is skipped in the listing
		add_host_with_interface('backend-0-1', '0', '2', 'backend', 'eth0')

		# Add a few for backend-0-1
		result = host.run('stack add host alias backend-0-1 alias=test-4 interface=eth0')
		assert result.rc == 0

		result = host.run('stack add host alias backend-0-1 alias=test-5 interface=eth0')
		assert result.rc == 0

		# Now, make sure only the frontend and backend-0-0 aliases are listed
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'alias': 'test-0',
				'interface': 'eth1'
			},
			{
				'host': 'frontend-0-0',
				'alias': 'test-1',
				'interface': 'eth1'
			},
			{
				'host': 'backend-0-0',
				'alias': 'test-2',
				'interface': 'eth0'
			},
			{
				'host': 'backend-0-0',
				'alias': 'test-3',
				'interface': 'eth0'
			}
		]

	def test_with_interface(self, host, add_host_with_interface):
		# Add an alias for the frontend, which should be skipped
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		# Add another interface to the backend
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add an alias for the backend on interface eth0
		result = host.run('stack add host alias backend-0-0 alias=test-1 interface=eth0')
		assert result.rc == 0

		# Add another for eth1
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth1')
		assert result.rc == 0

		# Do a listing on eth1, making sure eth0 doesn't show up
		result = host.run('stack list host alias backend-0-0 interface=eth1 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'backend-0-0',
				'alias': 'test-2',
				'interface': 'eth1'
			}
		]
