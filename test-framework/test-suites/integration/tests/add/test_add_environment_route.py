import json
from textwrap import dedent


class TestAddEnvironmentRoute:
	def test_no_args(self, host):
		result = host.run('stack add environment route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_environment(self, host):
		result = host.run(
			'stack add environment route address=192.168.0.2 gateway=192.168.0.1'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_address(self, host, add_environment):
		result = host.run(
			'stack add environment route test gateway=192.168.0.1'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{environment ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_gateway(self, host, add_environment):
		result = host.run(
			'stack add environment route test address=192.168.0.2'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "gateway" parameter is required
			{environment ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_with_subnet(self, host, add_environment):
		# Add the route
		result = host.run(
			'stack add environment route test address=192.168.0.2 gateway=private'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list environment route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"environment": "test",
			"network": "192.168.0.2",
			"netmask": "255.255.255.255",
			"gateway": None,
			"subnet": "private",
			"interface": None
		}]

	def test_with_gateway_and_netmask(self, host, add_environment):
		# Add the route
		result = host.run(
			'stack add environment route test address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list environment route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"environment": "test",
			"network": "192.168.0.2",
			"netmask": "255.255.255.0",
			"gateway": "192.168.0.1",
			"subnet": None,
			"interface": None
		}]

	def test_with_interface(self, host, add_environment):
		# Add the route
		result = host.run(
			'stack add environment route test address=192.168.0.2 '
			'gateway=192.168.0.1 interface=eth0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list environment route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"environment": "test",
			"network": "192.168.0.2",
			"netmask": "255.255.255.255",
			"gateway": "192.168.0.1",
			"subnet": None,
			"interface": 'eth0'
		}]

	def test_duplicate(self, host, add_environment):
		# Add the route
		result = host.run(
			'stack add environment route test address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Add it again and make sure it errors out
		result = host.run(
			'stack add environment route test address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 255
		assert result.stderr == 'error - route for "192.168.0.2" already exists\n'
