import json
from textwrap import dedent


class TestAddRoute:
	def test_no_address(self, host):
		result = host.run('stack add route gateway=192.168.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_no_gateway(self, host):
		result = host.run('stack add route address=192.168.0.2')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "gateway" parameter is required
			{address=string} {gateway=string} [interface=string] [netmask=string]
		''')

	def test_with_subnet(self, host):
		# Add the route
		result = host.run('stack add route address=192.168.0.2 gateway=private')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list route output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'subnet': 'private'
			}
		]

	def test_with_gateway_and_netmask(self, host):
		# Add the route
		result = host.run(
			'stack add route address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list route output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '192.168.0.1',
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '192.168.0.2',
				'subnet': None
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'subnet': 'private'
			}
		]

	def test_with_interface(self, host):
		# Add the route
		result = host.run(
			'stack add route address=192.168.0.2 gateway=192.168.0.1 interface=eth0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list route output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '192.168.0.1',
				'interface': 'eth0',
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'subnet': None
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'subnet': 'private'
			}
		]

	def test_duplicate(self, host):
		# Add the route
		result = host.run('stack add route address=192.168.0.2 gateway=192.168.0.1')
		assert result.rc == 0

		# Add it again and make sure it errors out
		result = host.run('stack add route address=192.168.0.2 gateway=192.168.0.1')
		assert result.rc == 255
		assert result.stderr == 'error - route for "192.168.0.2" already exists\n'
