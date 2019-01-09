import json
from textwrap import dedent


class TestAddOSRoute:
	def test_no_args(self, host):
		result = host.run('stack add os route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_os(self, host):
		result = host.run(
			'stack add os route address=192.168.0.2 gateway=192.168.0.1'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_address(self, host):
		result = host.run(
			'stack add os route ubuntu gateway=192.168.0.1'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{os ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_gateway(self, host):
		result = host.run(
			'stack add os route ubuntu address=192.168.0.2'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "gateway" parameter is required
			{os ...} {address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_with_subnet(self, host):
		# Add the route
		result = host.run(
			'stack add os route ubuntu address=192.168.0.2 gateway=private'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list os route ubuntu output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"os": "ubuntu",
			"network": "192.168.0.2",
			"netmask": "255.255.255.255",
			"gateway": None,
			"subnet": "private",
			"interface": None
		}]

	def test_with_gateway_and_netmask(self, host):
		# Add the route
		result = host.run(
			'stack add os route ubuntu address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list os route ubuntu output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"os": "ubuntu",
			"network": "192.168.0.2",
			"netmask": "255.255.255.0",
			"gateway": "192.168.0.1",
			"subnet": None,
			"interface": None
		}]

	def test_with_interface(self, host):
		# Add the route
		result = host.run(
			'stack add os route ubuntu address=192.168.0.2 '
			'gateway=192.168.0.1 interface=eth0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list os route ubuntu output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			"os": "ubuntu",
			"network": "192.168.0.2",
			"netmask": "255.255.255.255",
			"gateway": "192.168.0.1",
			"subnet": None,
			"interface": 'eth0'
		}]

	def test_duplicate(self, host):
		# Add the route
		result = host.run(
			'stack add os route ubuntu address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Add it again and make sure it errors out
		result = host.run(
			'stack add os route ubuntu address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 255
		assert result.stderr == 'error - route for "192.168.0.2" already exists\n'
