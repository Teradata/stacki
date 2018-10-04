import json
from textwrap import dedent


class TestSetHostInterfaceDefault:
	def test_no_hosts(self, host):
		result = host.run('stack set host interface default')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [default=boolean] [interface=string] [mac=string] [network=string]
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack set host interface default a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} [default=boolean] [interface=string] [mac=string] [network=string]
		''')

	def test_no_selector(self, host):
		result = host.run('stack set host interface default frontend-0-0 channel=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "mac" or "network" parameter is required
			{host ...} [default=boolean] [interface=string] [mac=string] [network=string]
		''')

	def test_invalid_interface(self, host):
		result = host.run('stack set host interface default frontend-0-0 interface=eth9 channel=1')
		assert result.rc == 255
		assert result.stderr == 'error - interface "eth9" does not exist for host "frontend-0-0"\n'

	def test_invalid_mac(self, host):
		result = host.run('stack set host interface default frontend-0-0 mac=00:11:22:33:44:55 channel=1')
		assert result.rc == 255
		assert result.stderr == 'error - mac "00:11:22:33:44:55" does not exist for host "frontend-0-0"\n'

	def test_invalid_network(self, host):
		result = host.run('stack set host interface default frontend-0-0 network=test channel=1')
		assert result.rc == 255
		assert result.stderr == 'error - network "test" does not exist for host "frontend-0-0"\n'

	def test_invalid_combo(self, host, add_host, add_network):
		# Add an interface with an interface and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Add a second interface with an interface and a mac to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth1 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Now try to set the data with a bad combo
		result = host.run(
			'stack set host interface default backend-0-0 network=test interface=eth1 channel=1'
		)
		assert result.rc == 255
		assert result.stderr == 'error - combination of "eth1, test" does not exist for host "backend-0-0"\n'

	def test_by_network(self, host, add_host, add_network):
		# Add an interface with an interface and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Set the default host interface
		result = host.run('stack set host interface default backend-0-0 network=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': True,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': None,
			'mac': None,
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_by_interface(self, host, add_host_with_interface):
		# Set the default host interface
		result = host.run('stack set host interface default backend-0-0 interface=eth0')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': True,
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

		# Now set the default back to false
		result = host.run('stack set host interface default backend-0-0 interface=eth0 default=false')
		assert result.rc == 0

		# Did it stick?
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
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
		}]

	def test_by_mac(self, host, add_host):
		# Add an interface with a mac to our test host
		result = host.run('stack add host interface backend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Set the default host interface
		result = host.run('stack set host interface default backend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': True,
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

	def test_all_parameters(self, host, add_host, add_network):
		# Add an interface with an interface, mac, and network to our test host
		result = host.run(
			'stack add host interface backend-0-0 interface=eth0 '
			'mac=00:11:22:33:44:55 network=test'
		)
		assert result.rc == 0

		# Set the default host interface
		result = host.run(
			'stack set host interface default backend-0-0 interface=eth0 '
			'mac=00:11:22:33:44:55 network=test'
		)
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': True,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': None,
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_multiple_hosts(self, host, add_host_with_interface):
		# Add a second test backend
		add_host_with_interface('backend-0-1', '0', '1', 'backend', 'eth0')

		# Set the default host interface on both backends
		result = host.run('stack set host interface default backend-0-0 backend-0-1 interface=eth0')
		assert result.rc == 0

		# Check that the changes made it into the database
		result = host.run('stack list host interface a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': True,
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
				'channel': None,
				'default': True,
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
