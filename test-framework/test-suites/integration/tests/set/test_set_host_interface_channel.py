import json
from textwrap import dedent


class TestSetHostInterfaceChannel:
	def test_set_host_interface_channel_no_hosts(self, host):
		result = host.run('stack set host interface channel')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {environment=string}
		''')

	def test_set_host_interface_channel_no_matching_hosts(self, host):
		result = host.run('stack set host interface channel a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {environment=string}
		''')

	def test_set_host_interface_channel_no_parameters(self, host):
		result = host.run('stack set host interface channel frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "channel" parameter is required
			{host ...} {channel=string} [interface=string] [mac=string]
		''')

	def test_set_host_interface_channel_no_interface_or_mac(self, host):
		result = host.run('stack set host interface channel frontend-0-0 channel=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "mac" parameter is required
			{host ...} {channel=string} [interface=string] [mac=string]
		''')

	def test_set_host_interface_channel_invalid_interface(self, host):
		result = host.run('stack set host interface channel frontend-0-0 interface=eth9 channel=1')
		assert result.rc == 255
		assert result.stderr == 'error - interface "eth9" does not exist for host "frontend-0-0"\n'

	def test_set_host_interface_channel_invalid_mac(self, host):
		result = host.run('stack set host interface channel frontend-0-0 mac=00:11:22:33:44:55 channel=1')
		assert result.rc == 255
		assert result.stderr == 'error - mac "00:11:22:33:44:55" does not exist for host "frontend-0-0"\n'

	def test_set_host_interface_channel_by_interface(self, host, add_host_with_interface):
		# Set the host interface channel
		result = host.run('stack set host interface channel backend-0-0 interface=eth0 channel=1')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': '1',
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': None,
			'mac': None,
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

	def test_set_host_interface_channel_by_mac(self, host, add_host):
		# Add an interface with a mac to our test host
		result = host.run('stack add host interface backend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Set the host interface channel
		result = host.run('stack set host interface channel backend-0-0 mac=00:11:22:33:44:55 channel=1')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': '1',
			'default': None,
			'host': 'backend-0-0',
			'interface': None,
			'ip': None,
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

	def test_set_host_interface_channel_multiple_hosts(self, host, add_host_with_interface):
		# Add a second test backend
		add_host_with_interface('backend-0-1', '0', '1', 'backend', 'eth0')

		# Set the host interface channel on both backends
		result = host.run('stack set host interface channel backend-0-0 backend-0-1 interface=eth0 channel=1')
		assert result.rc == 0

		# Check that the changes made it into the database
		result = host.run('stack list host interface a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': '1',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': '1',
				'default': None,
				'host': 'backend-0-1',
				'interface': 'eth0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			}
		]
