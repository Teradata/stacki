import json
from textwrap import dedent


class TestSetNetworkName:
	def test_no_networks(self, host):
		result = host.run('stack set network name')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network} {name=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set network name private')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "name" parameter is required
			{network} {name=string}
		''')

	def test_invalid_network(self, host):
		result = host.run('stack set network name test address=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network} {name=string}
		''')

	def test_invalid_name(self, host, add_network):
		result = host.run('stack set network name test name="foo bar"')
		assert result.rc == 255
		assert result.stderr == 'error - network name must not contain a space\n'

	def test_single_host(self, host, add_network):
		# Set the network name
		result = host.run('stack set network name test name=foo')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list network foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'network': 'foo',
			'address': '192.168.0.0',
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

		# Set the network name on both networks, which should error out
		result = host.run('stack set network name test foo name=bar')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument must be unique
			{network} {name=string}
		''')
