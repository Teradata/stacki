import json
from textwrap import dedent


class TestSetNetworkAddress:
	def test_no_networks(self, host):
		result = host.run('stack set network address')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network} {address=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set network address private')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{network} {address=string}
		''')

	def test_invalid_network(self, host):
		result = host.run('stack set network address test address=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network} {address=string}
		''')

	def test_invalid_address(self, host, add_network):
		result = host.run('stack set network address test address=999.0.0.1')
		assert result.rc == 255
		assert result.stderr == (
			'error - 999.0.0.1/255.255.255.0 is not a valid network '
			'address and subnet mask combination\n'
		)

	def test_single_host(self, host, add_network):
		# Set the network address
		result = host.run('stack set network address test address=10.10.10.0')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'network': 'test',
			'address': '10.10.10.0',
			'mask': '255.255.255.0',
			'gateway': '',
			'mtu': None,
			'zone': 'test',
			'dns': False,
			'pxe': False
		}]

	def test_multiple_hosts(self, host, add_network):
		# Add a second test network
		add_network('foo', '192.168.1.0')

		# Set the network address on both networks, which should error out
		result = host.run('stack set network address test foo address=10.10.10.0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument must be unique
			{network} {address=string}
		''')
