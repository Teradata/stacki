import json
from textwrap import dedent


class TestRemoveEnvironmentRoute:
	def test_no_args(self, host):
		result = host.run('stack remove environment route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {address=string}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove environment route test address=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid environment
			{environment ...} {address=string}
		''')

	def test_no_address(self, host, add_environment):
		result = host.run('stack remove environment route test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{environment ...} {address=string}
		''')

	def test_one_arg(self, host, add_environment):
		# Add a couple environment routes
		result = host.run('stack add environment route test address=192.168.0.2 gateway=private')
		assert result.rc == 0

		result = host.run('stack add environment route test address=192.168.0.3 gateway=private')
		assert result.rc == 0

		# Confirm they are there
		result = host.run('stack list environment route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"environment": "test",
				"network": "192.168.0.2",
				"netmask": "255.255.255.255",
				"gateway": None,
				"subnet": "private",
				"interface": None
			},
			{
				"environment": "test",
				"network": "192.168.0.3",
				"netmask": "255.255.255.255",
				"gateway": None,
				"subnet": "private",
				"interface": None
			}
		]

		# Now remove the first environment route added
		result = host.run('stack remove environment route test address=192.168.0.2')
		assert result.rc == 0

		# Make sure only one route was removed
		result = host.run('stack list environment route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"environment": "test",
				"network": "192.168.0.3",
				"netmask": "255.255.255.255",
				"gateway": None,
				"subnet": "private",
				"interface": None
			}
		]

	def test_multiple_args(self, host, add_environment):
		# Add a couple environment routes to the "test" environment
		result = host.run('stack add environment route test address=192.168.0.2 gateway=private')
		assert result.rc == 0

		result = host.run('stack add environment route test address=192.168.0.3 gateway=private')
		assert result.rc == 0

		# Add a second test environment
		add_environment('foo')

		# Add a couple environment routes to the "foo" environment
		result = host.run('stack add environment route foo address=192.168.0.4 gateway=private')
		assert result.rc == 0

		result = host.run('stack add environment route foo address=192.168.0.5 gateway=private')
		assert result.rc == 0

		# Confirm all our routes are there
		result = host.run('stack list environment route test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'environment': 'foo',
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.4',
				'subnet': 'private'
			},
			{
				'environment': 'foo',
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.5',
				'subnet': 'private'
			},
			{
				'environment': 'test',
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'subnet': 'private'
			},
			{
				'environment': 'test',
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.3',
				'subnet': 'private'
			}
		]

		# Now remove the second route added to "test" environment
		result = host.run('stack remove environment route test address=192.168.0.3')
		assert result.rc == 0

		# And the first added to "foo" environment
		result = host.run('stack remove environment route foo address=192.168.0.4')
		assert result.rc == 0

		# Make sure only the expected routes were removed
		result = host.run('stack list environment route test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'environment': 'foo',
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.5',
				'subnet': 'private'
			},
			{
				'environment': 'test',
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'subnet': 'private'
			}
		]
