import json
from textwrap import dedent


class TestRemoveHostInterface:
	def test_invalid_host(self, host):
		result = host.run('stack remove host interface test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_no_args(self, host):
		result = host.run('stack remove host interface')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			[host ...] [all=bool] [interface=string] [mac=string]
		''')

	def test_no_host_matches(self, host):
		result = host.run('stack remove host interface a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			[host ...] [all=bool] [interface=string] [mac=string]
		''')

	def test_no_parameters(self, host, add_host_with_interface):
		result = host.run('stack remove host interface backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "mac" parameter is required
			[host ...] [all=bool] [interface=string] [mac=string]
		''')

	def test_invalid_interface(self, host, add_host):
		result = host.run('stack remove host interface backend-0-0 interface=eth0')
		assert result.rc == 255
		assert result.stderr == 'error - no interface "eth0" exists on backend-0-0\n'

	def test_invalid_mac(self, host, add_host):
		result = host.run('stack remove host interface backend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 255
		assert result.stderr == 'error - no mac address "00:11:22:33:44:55" exists on backend-0-0\n'

	def test_single_arg(self, host, add_host_with_interface):
		# Add a second interface which shouldn't get removed
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Remove the eth0 interface from our host
		result = host.run('stack remove host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# Confirm it is removed
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': None,
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			}
		]

	def test_multiple_args(self, host, add_host_with_interface):
		# Add a second interface which shouldn't get removed
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add a second host with an interface
		add_host_with_interface('backend-0-1', '0', '2', 'backend', 'eth0')

		# It can have a second interface too
		result = host.run('stack add host interface backend-0-1 interface=eth1')
		assert result.rc == 0

		# Remove the eth0 interface from our hosts
		result = host.run('stack remove host interface backend-0-0 backend-0-1 interface=eth0')
		assert result.rc == 0

		# Confirm it is removed
		result = host.run('stack list host interface backend-0-0 backend-0-1 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': None,
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-1',
				'interface': 'eth1',
				'ip': None,
				'mac': None,
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			}
		]

	def test_with_mac(self, host, add_host_with_interface):
		# Add a second interface which shouldn't get removed
		result = host.run('stack add host interface backend-0-0 interface=eth1 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Remove the eth1 interface from our host using mac
		result = host.run('stack remove host interface backend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Confirm it is removed
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
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
			}
		]

	def test_with_all(self, host, add_host_with_interface):
		# Add a second interface which should get removed as well
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add a second host with an interface, which shouldn't get touched
		add_host_with_interface('backend-0-1', '0', '2', 'backend', 'eth0')

		# Remove all the interfaces from our host using mac
		result = host.run('stack remove host interface backend-0-0 all=true')
		assert result.rc == 0

		# Confirm only backend-0-0 interfaces were removed
		result = host.run('stack list host interface backend-0-0 backend-0-1 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
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
