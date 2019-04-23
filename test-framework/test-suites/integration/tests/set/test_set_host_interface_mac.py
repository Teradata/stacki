import json
from textwrap import dedent


class TestSetHostInterfaceMac:
	def test_no_hosts(self, host):
		result = host.run('stack set host interface mac')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {mac=string} [interface=string] [network=string]
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack set host interface mac a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {mac=string} [interface=string] [network=string]
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set host interface mac frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "mac" parameter is required
			{host} {mac=string} [interface=string] [network=string]
		''')

	def test_no_selector(self, host):
		result = host.run('stack set host interface mac frontend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "network" parameter is required
			{host} {mac=string} [interface=string] [network=string]
		''')

	def test_invalid_interface(self, host):
		result = host.run('stack set host interface mac frontend-0-0 interface=eth9 mac=00:11:22:33:44:55')
		assert result.rc == 255
		assert result.stderr == 'error - interface "eth9" does not exist for host "frontend-0-0"\n'

	def test_invalid_network(self, host):
		result = host.run('stack set host interface mac frontend-0-0 network=test mac=00:11:22:33:44:55')
		assert result.rc == 255
		assert result.stderr == 'error - network "test" does not exist for host "frontend-0-0"\n'

	def test_invalid_combo(self, host, add_host, add_network):
		# Add an interface with an interface and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Add a second interface with interface to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Now try to set the data with a bad combo
		result = host.run(
			'stack set host interface mac backend-0-0 interface=eth1 network=test mac=00:11:22:33:44:55'
		)
		assert result.rc == 255
		assert result.stderr == 'error - combination of "eth1, test" does not exist for host "backend-0-0"\n'

	def test_by_network(self, host, add_host, add_network):
		# Add an interface with a interface device and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Set the host interface mac
		result = host.run('stack set host interface mac backend-0-0 mac=00:11:22:33:44:55 network=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
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

	def test_by_interface(self, host, add_host_with_interface):
		# Set the host interface mac
		result = host.run('stack set host interface mac backend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': None,
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

		# Now set the mac back to NULL
		result = host.run('stack set host interface mac backend-0-0 interface=eth0 mac=null')
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

	def test_all_parameters(self, host, add_host, add_network):
		# Add an interface with a interface device and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Set the host interface mac
		result = host.run(
			'stack set host interface mac backend-0-0 interface=eth0 '
			'mac=00:11:22:33:44:55 network=test'
		)
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
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

	def test_all_parameters_insensitive(self, host, add_host, add_network):
		# Add an interface with a interface device and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Set the host interface mac
		result = host.run(
			'stack set host interface mac backend-0-0 interface=ETH0 '
			'mac=aa:bb:cc:dd:ee:ff network=TEST'
		)
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': None,
			'mac': 'aa:bb:cc:dd:ee:ff',
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_multiple_hosts(self, host, add_host):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Try to set the mac on multiple hosts
		result = host.run('stack set host interface mac backend-0-0 backend-0-1 mac=00:11:22:33:44:55')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} {mac=string} [interface=string] [network=string]
		''')
