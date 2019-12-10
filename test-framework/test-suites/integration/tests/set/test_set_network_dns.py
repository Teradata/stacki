import json
from textwrap import dedent


class TestSetNetworkDNS:
	def test_no_networks(self, host):
		result = host.run('stack set network dns')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network ...} {dns=boolean}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set network dns private')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "dns" parameter is required
			{network ...} {dns=boolean}
		''')

	def test_invalid_network(self, host):
		result = host.run('stack set network dns test dns=true')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network ...} {dns=boolean}
		''')

	def test_single_host(self, host, add_network):
		# Set the network dns to True
		result = host.run('stack set network dns test dns=true')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'network': 'test',
			'address': '192.168.0.0',
			'mask': '255.255.255.0',
			'gateway': '',
			'mtu': None,
			'zone': 'test',
			'dns': True,
			'pxe': False
		}]

	def test_multiple_hosts(self, host, add_network):
		# Add a second test network
		add_network('foo', '192.168.1.0')

		# Set the network dns on both networks
		result = host.run('stack set network dns test foo dns=true')
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
				'mtu': None,
				'zone': 'test',
				'dns': True,
				'pxe': False
			},
			{
				'network': 'foo',
				'address': '192.168.1.0',
				'mask': '255.255.255.0',
				'gateway': '',
				'mtu': None,
				'zone': 'foo',
				'dns': True,
				'pxe': False
			}
		]
