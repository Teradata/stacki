import json
from textwrap import dedent


class TestAddHostRoute:
	def test_no_args(self, host):
		result = host.run('stack add host route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {address=string} {gateway=string} [interface=string] [netmask=string] [syncnow=string]
		''')

	def test_no_host(self, host):
		result = host.run(
			'stack add host route address=192.168.0.2 gateway=192.168.0.1'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {address=string} {gateway=string} [interface=string] [netmask=string] [syncnow=string]
		''')

	def test_no_address(self, host):
		result = host.run(
			'stack add host route frontend-0-0 gateway=192.168.0.1'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{host ...} {address=string} {gateway=string} [interface=string] [netmask=string] [syncnow=string]
		''')

	def test_no_gateway(self, host):
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.2'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "gateway" parameter is required
			{host ...} {address=string} {gateway=string} [interface=string] [netmask=string] [syncnow=string]
		''')

	def test_with_subnet(self, host):
		# Add the route
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.2 gateway=private'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'source': 'H',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

	def test_with_gateway_and_netmask(self, host):
		# Add the route
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '192.168.0.1',
				'host': 'frontend-0-0',
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '192.168.0.2',
				'source': 'H',
				'subnet': None
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

	def test_with_interface(self, host):
		# Add the route
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.2 '
			'gateway=192.168.0.1 interface=eth0'
		)
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '192.168.0.1',
				'host': 'frontend-0-0',
				'interface': 'eth0',
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'source': 'H',
				'subnet': None
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

	def test_duplicate(self, host, add_environment):
		# Add the route
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 0

		# Add it again and make sure it errors out
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.2 '
			'gateway=192.168.0.1 netmask=255.255.255.0'
		)
		assert result.rc == 255
		assert result.stderr == 'error - route for "192.168.0.2" already exists\n'

	def test_with_syncnow(self, host, revert_routing_table, revert_etc):
		# Add a route with sync now so it is added to the routing table
		result = host.run(
			'stack add host route frontend-0-0 address=192.168.0.3 '
			'gateway=192.168.0.2 interface=eth1 syncnow=true'
		)
		assert result.rc == 0

		# Confirm it is in the DB
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{'gateway': '192.168.0.2',
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '192.168.0.3',
				'source': 'H',
				'subnet': None
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

		# Also check that the test route is in our routing table
		result = host.run('ip route list')
		assert result.rc == 0
		assert '192.168.0.3 via 192.168.0.2 dev eth1' in result.stdout
