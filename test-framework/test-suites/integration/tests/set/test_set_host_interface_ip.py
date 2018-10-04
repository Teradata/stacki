import json
from textwrap import dedent


class TestSetHostInterfaceIP:
	def test_no_hosts(self, host):
		result = host.run('stack set host interface ip')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {ip=string} [interface=string] [mac=string] [network=string]
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack set host interface ip a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {ip=string} [interface=string] [mac=string] [network=string]
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set host interface ip frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "ip" parameter is required
			{host} {ip=string} [interface=string] [mac=string] [network=string]
		''')

	def test_no_selector(self, host):
		result = host.run('stack set host interface ip frontend-0-0 ip=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "mac" or "network" parameter is required
			{host} {ip=string} [interface=string] [mac=string] [network=string]
		''')

	def test_invalid_interface(self, host):
		result = host.run('stack set host interface ip frontend-0-0 interface=eth9 ip=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == 'error - interface "eth9" does not exist for host "frontend-0-0"\n'

	def test_invalid_mac(self, host):
		result = host.run('stack set host interface ip frontend-0-0 mac=00:11:22:33:44:55 ip=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == 'error - mac "00:11:22:33:44:55" does not exist for host "frontend-0-0"\n'

	def test_invalid_network(self, host):
		result = host.run('stack set host interface ip frontend-0-0 network=test ip=127.0.0.1')
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
			'stack set host interface ip backend-0-0 network=test interface=eth1 ip=127.0.0.1'
		)
		assert result.rc == 255
		assert result.stderr == 'error - combination of "eth1, test" does not exist for host "backend-0-0"\n'

	def test_by_network(self, host, add_host, add_network):
		# Add an interface with an interface and network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		# Set the host IP address
		result = host.run('stack set host interface ip backend-0-0 network=test ip=192.168.0.2')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': '192.168.0.2',
			'mac': None,
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_by_interface(self, host, add_host_with_interface):
		# Set the host IP address
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=192.168.0.2')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': '192.168.0.2',
			'mac': None,
			'module': None,
			'name': None,
			'network': None,
			'options': None,
			'vlan': None
		}]

		# Now set the ip back to NULL
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=null')
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

		# Set the host IP address
		result = host.run('stack set host interface ip backend-0-0 mac=00:11:22:33:44:55 ip=192.168.0.2')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': None,
			'ip': '192.168.0.2',
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

		# Set the host IP address
		result = host.run(
			'stack set host interface ip backend-0-0 interface=eth0 '
			'mac=00:11:22:33:44:55 network=test ip=192.168.0.2'
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
			'ip': '192.168.0.2',
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_by_network_with_auto(self, host, add_host):
		# Create a test network with a whole class A block
		result = host.run('stack add network test address=10.0.0.0 mask=255.0.0.0 gateway=10.0.0.1')
		assert result.rc == 0

		# Add another test host whose IP should get skipped
		add_host('backend-0-1', '0', '1', 'backend')

		# Add an interface with an interface and network to our test hosts
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-1 interface=eth0 network=test')
		assert result.rc == 0

		# Set the IP address on the second test host
		result = host.run('stack set host interface ip backend-0-1 network=test ip=10.0.0.2')
		assert result.rc == 0

		# Set the first test host IP address using AUTO
		result = host.run('stack set host interface ip backend-0-0 network=test ip=auto')
		assert result.rc == 0

		# Check that it made it into the database with the expected IP
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': '10.0.0.3',
			'mac': None,
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_by_interface_with_auto(self, host, add_host):
		# Create a test network with a whole class A block
		result = host.run('stack add network test address=10.0.0.0 mask=255.0.0.0 gateway=10.0.0.1')
		assert result.rc == 0

		# Add another test host whose IP should get skipped
		add_host('backend-0-1', '0', '1', 'backend')

		# Add an interface with an interface and network to our test hosts
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-1 interface=eth0 network=test')
		assert result.rc == 0

		# Set the IP address on the second test host
		result = host.run('stack set host interface ip backend-0-1 interface=eth0 ip=10.0.0.2')
		assert result.rc == 0

		# Set the first test host IP address using AUTO
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=auto')
		assert result.rc == 0

		# Check that it made it into the database with the expected IP
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': 'eth0',
			'ip': '10.0.0.3',
			'mac': None,
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_by_mac_with_auto(self, host, add_host):
		# Create a test network with a whole class A block
		result = host.run('stack add network test address=10.0.0.0 mask=255.0.0.0 gateway=10.0.0.1')
		assert result.rc == 0

		# Add another test host whose IP should get skipped
		add_host('backend-0-1', '0', '1', 'backend')

		# Add an interface with a mac and network to our first test host
		result = host.run('stack add host interface backend-0-0 mac=00:11:22:33:44:55 network=test')
		assert result.rc == 0

		# Add an interface with a different mac to our second test host
		result = host.run('stack add host interface backend-0-1 mac=AA:BB:CC:DD:EE:FF network=test')
		assert result.rc == 0

		# Set the IP address on the second test host
		result = host.run('stack set host interface ip backend-0-1 mac=AA:BB:CC:DD:EE:FF ip=10.0.0.2')
		assert result.rc == 0

		# Set the first test host IP address using AUTO
		result = host.run('stack set host interface ip backend-0-0 mac=00:11:22:33:44:55 ip=auto')
		assert result.rc == 0

		# Check that it made it into the database with the expected IP
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'channel': None,
			'default': None,
			'host': 'backend-0-0',
			'interface': None,
			'ip': '10.0.0.3',
			'mac': '00:11:22:33:44:55',
			'module': None,
			'name': None,
			'network': 'test',
			'options': None,
			'vlan': None
		}]

	def test_auto_without_network(self, host, add_host):
		# Create a test network with a whole class A block
		result = host.run('stack add network test address=10.0.0.0 mask=255.0.0.0 gateway=10.0.0.1')
		assert result.rc == 0

		# Add an interface with an interface but without a network to our test host
		result = host.run('stack add host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# Try to set the host IP address using AUTO
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=auto')
		assert result.rc == 255
		assert result.stderr == 'error - unknown network for interface\n'

	def test_auto_no_more_ips(self, host, add_host):
		# Create a very small test network
		result = host.run('stack add network test address=192.168.0.0 mask=255.255.255.252 gateway=192.168.0.1')
		assert result.rc == 0

		# Add another test host whose IP should get skipped
		add_host('backend-0-1', '0', '1', 'backend')

		# Add an interface with an interface device and network to our test hosts
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-1 interface=eth0 network=test')
		assert result.rc == 0

		# Set the IP address on the second test host, which is the last available
		result = host.run('stack set host interface ip backend-0-1 interface=eth0 ip=192.168.0.2')
		assert result.rc == 0

		# Set the first test host IP address using AUTO, which should throw an error
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=auto')
		assert result.rc == 255
		assert result.stderr == 'error - no free ip addresses left in the network\n'

	def test_multiple_hosts(self, host, add_host):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Try to set the ip on multiple hosts
		result = host.run('stack set host interface ip backend-0-0 backend-0-1 ip=192.168.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} {ip=string} [interface=string] [mac=string] [network=string]
		''')
