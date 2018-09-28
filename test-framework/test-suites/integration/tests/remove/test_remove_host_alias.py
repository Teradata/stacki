import json
from textwrap import dedent


class TestRemoveHostAlias:
	def test_remove_host_alias_invalid_host(self, host):
		result = host.run('stack remove host alias test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_remove_host_alias_no_args(self, host):
		result = host.run('stack remove host alias')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [alias=string] [interface=string]
		''')

	def test_remove_host_alias_no_host_matches(self, host):
		result = host.run('stack remove host alias a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [alias=string] [interface=string]
		''')

	def test_remove_host_alias_multiple_args(self, host, add_host_with_interface):
		result = host.run('stack remove host alias frontend-0-0 backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} [alias=string] [interface=string]
		''')

	def test_remove_host_alias_no_parameters(self, host, add_host_with_interface):
		# Add a few aliases for the frontend
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		result = host.run('stack add host alias frontend-0-0 alias=test-1 interface=eth1')
		assert result.rc == 0

		# Add one for the backend so we can make sure remove leaves it alone
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth0')
		assert result.rc == 0

		# Confirm all our aliases are in the DB
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
			}
		]

		# Do a remove without specifying alias or interface
		result = host.run('stack remove host alias frontend-0-0')
		assert result.rc == 0

		# Confirm only the backend alias remains
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'backend-0-0',
				'alias': 'test-2',
				'interface': 'eth0'
			}
		]

	def test_remove_host_alias_with_alias(self, host, add_host_with_interface):
		# Add a few aliases for the frontend
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		result = host.run('stack add host alias frontend-0-0 alias=test-1 interface=eth1')
		assert result.rc == 0

		# Add one for the backend so we can make sure remove leaves it alone
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth0')
		assert result.rc == 0

		# Confirm all our aliases are in the DB
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
			}
		]

		# Do a remove specifying the alias
		result = host.run('stack remove host alias frontend-0-0 alias=test-1')
		assert result.rc == 0

		# Confirm only the test-1 alias was removed
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'alias': 'test-0',
				'interface': 'eth1'
			},
			{
				'host': 'backend-0-0',
				'alias': 'test-2',
				'interface': 'eth0'
			}
		]

	def test_remove_host_alias_with_interface(self, host, add_host_with_interface):
		# Add an alias for the frontend
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		# Add one for the backend so we can make sure remove leaves it alone
		result = host.run('stack add host alias backend-0-0 alias=test-1 interface=eth0')
		assert result.rc == 0

		# Add a second interface to the backend
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add an alias for the new backend interface, which we will be removeing
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth1')
		assert result.rc == 0

		# Confirm all our aliases are in the DB
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
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
			},
			{
				'host': 'backend-0-0',
				'alias': 'test-2',
				'interface': 'eth1'
			}
		]

		# Do a remove specifying the interface
		result = host.run('stack remove host alias backend-0-0 interface=eth1')
		assert result.rc == 0

		# Confirm only the test-2 alias was removed
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
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

	def test_remove_host_alias_with_alias_and_interface(self, host, add_host_with_interface):
		# Add an alias for the frontend
		result = host.run('stack add host alias frontend-0-0 alias=test-0 interface=eth1')
		assert result.rc == 0

		# Add one for the backend so we can make sure remove leaves it alone
		result = host.run('stack add host alias backend-0-0 alias=test-1 interface=eth0')
		assert result.rc == 0

		# Add a second interface to the backend
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add an alias for the new backend interface, which we will be removeing
		result = host.run('stack add host alias backend-0-0 alias=test-2 interface=eth1')
		assert result.rc == 0

		# Confirm all our aliases are in the DB
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
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
			},
			{
				'host': 'backend-0-0',
				'alias': 'test-2',
				'interface': 'eth1'
			}
		]

		# Do a remove specifying the interface
		result = host.run('stack remove host alias backend-0-0 alias=test-2 interface=eth1')
		assert result.rc == 0

		# Confirm only the test-2 alias was removed
		result = host.run('stack list host alias frontend-0-0 backend-0-0 output-format=json')
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
