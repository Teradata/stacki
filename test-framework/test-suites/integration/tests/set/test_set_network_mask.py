import json
from textwrap import dedent


class TestSetNetworkMask:
	def test_no_networks(self, host):
		result = host.run('stack set network mask')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network ...} {mask=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set network mask private')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "mask" parameter is required
			{network ...} {mask=string}
		''')

	def test_invalid_network(self, host):
		result = host.run('stack set network mask test dns=true')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network ...} {mask=string}
		''')

	def test_single_host(self, host, add_network):
		# Set the network mask
		result = host.run('stack set network mask test mask=255.0.0.0')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'network': 'test',
			'address': '192.168.0.0',
			'mask': '255.0.0.0',
			'gateway': '',
			'mtu': None,
			'zone': 'test',
			'dns': False,
			'pxe': False
		}]

	def test_multiple_hosts(self, host, add_network):
		# Add a second test network
		add_network('foo', '192.168.1.0')

		# Set the network mask on both networks
		result = host.run('stack set network mask test foo mask=255.0.0.0')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'network': 'test',
				'address': '192.168.0.0',
				'mask': '255.0.0.0',
				'gateway': '',
				'mtu': None,
				'zone': 'test',
				'dns': False,
				'pxe': False
			},
			{
				'network': 'foo',
				'address': '192.168.1.0',
				'mask': '255.0.0.0',
				'gateway': '',
				'mtu': None,
				'zone': 'foo',
				'dns': False,
				'pxe': False
			}
		]
