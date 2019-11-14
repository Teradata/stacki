import json
from textwrap import dedent


class TestSetNetworkMTU:
	def test_no_networks(self, host):
		result = host.run('stack set network mtu')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network ...} {mtu=integer}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set network mtu private')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "mtu" parameter is required
			{network ...} {mtu=integer}
		''')

	def test_invalid_network(self, host):
		result = host.run('stack set network mtu test dns=true')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network ...} {mtu=integer}
		''')

	def test_single_host(self, host, add_network):
		# Set the network mtu
		result = host.run('stack set network mtu test mtu=9000')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'network': 'test',
			'address': '192.168.0.0',
			'mask': '255.255.255.0',
			'gateway': '',
			'mtu': 9000,
			'zone': 'test',
			'dns': False,
			'pxe': False
		}]

	def test_multiple_hosts(self, host, add_network):
		# Add a second test network
		add_network('foo', '192.168.1.0')

		# Set the network mtu on both networks
		result = host.run('stack set network mtu test foo mtu=9000')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'network': 'test',
				'address': '192.168.0.0',
				'mask': '255.255.255.0',
				'gateway': '',
				'mtu': 9000,
				'zone': 'test',
				'dns': False,
				'pxe': False
			},
			{
				'network': 'foo',
				'address': '192.168.1.0',
				'mask': '255.255.255.0',
				'gateway': '',
				'mtu': 9000,
				'zone': 'foo',
				'dns': False,
				'pxe': False
			}
		]
