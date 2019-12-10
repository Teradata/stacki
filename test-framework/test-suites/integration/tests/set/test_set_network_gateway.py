import json
from textwrap import dedent


class TestSetNetworkGateway:
	def test_no_networks(self, host):
		result = host.run('stack set network gateway')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network} {gateway=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set network gateway private')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "gateway" parameter is required
			{network} {gateway=string}
		''')

	def test_invalid_network(self, host):
		result = host.run('stack set network gateway test gateway=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network} {gateway=string}
		''')

	def test_single_host(self, host, add_network):
		# Set the network gateway
		result = host.run('stack set network gateway test gateway=192.168.0.1')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'network': 'test',
			'address': '192.168.0.0',
			'mask': '255.255.255.0',
			'gateway': '192.168.0.1',
			'mtu': None,
			'zone': 'test',
			'dns': False,
			'pxe': False
		}]

	def test_multiple_hosts(self, host, add_network):
		# Add a second test network
		add_network('foo', '192.168.1.0')

		# Set the network gateway on both networks, which should error out
		result = host.run('stack set network gateway test foo gateway=192.168.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument must be unique
			{network} {gateway=string}
		''')
