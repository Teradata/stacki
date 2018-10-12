import json
from textwrap import dedent

import pytest


@pytest.mark.usefixtures("add_host_with_interface")
class TestAddHostBonded:
	def test_no_hosts(self, host):
		result = host.run('stack add host bonded')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_no_matching_hosts(self, host):
		result = host.run('stack add host bonded a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_multiple_hosts(self, host):
		result = host.run('stack add host bonded frontend-0-0 backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_no_channel(self, host):
		result = host.run('stack add host bonded backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "channel" parameter is required
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_no_interfaces(self, host):
		result = host.run('stack add host bonded backend-0-0 channel=bond0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interfaces" parameter is required
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_no_ip(self, host):
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces=eth0,eth1')

		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "ip" parameter is required
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_no_network(self, host):
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces=eth0,eth1 ip=192.168.0.1')

		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" parameter is required
			{host} [channel=string] [interfaces=string] [ip=string] [name=string] [network=string] [options=string]
		''')
	
	def test_invalid_network(self, host):
		# Add a second interface to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0
		
		# Add the bonded interface
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces=eth0,eth1 ip=192.168.0.1 network=test')
		
		assert result.rc == 255
		assert result.stderr == 'error - network "test" does not exist\n'

	def test_missing_interface(self, host):
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces=eth0,eth1 ip=192.168.0.1 network=private')
		
		assert result.rc == 255
		assert result.stderr == 'error - interface "eth1" does not exist for host "backend-0-0"\n'

	def test_comma_seperated_interfaces(self, host):
		# Add a second interface to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add the bonded interface
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces=eth0,eth1 ip=192.168.0.1 network=private')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'bond0',
				'ip': '192.168.0.1',
				'mac': None,
				'module': 'bonding',
				'name': 'backend-0-0',
				'network': 'private',
				'options': None,
				'vlan': None
			},
			{
				'channel': 'bond0',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': 'bond0',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			}
		]

	def test_space_seperated_interfaces(self, host):
		# Add a second interface to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth1')
		assert result.rc == 0

		# Add the bonded interface
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces="eth0 eth1" ip=192.168.0.1 network=private')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'bond0',
				'ip': '192.168.0.1',
				'mac': None,
				'module': 'bonding',
				'name': 'backend-0-0',
				'network': 'private',
				'options': None,
				'vlan': None
			},
			{
				'channel': 'bond0',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': 'bond0',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			}
		]

	def test_default_with_options(self, host):
		# Add a second interface to our backend
		result = host.run('stack add host interface backend-0-0 interface=eth1 default=true')
		assert result.rc == 0

		# Add the bonded interface
		result = host.run('stack add host bonded backend-0-0 channel=bond0 '
		'interfaces=eth0,eth1 ip=192.168.0.1 network=private options=test_options')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': True,
				'host': 'backend-0-0',
				'interface': 'bond0',
				'ip': '192.168.0.1',
				'mac': None,
				'module': 'bonding',
				'name': 'backend-0-0',
				'network': 'private',
				'options': 'bonding-opts="test_options"',
				'vlan': None
			},
			{
				'channel': 'bond0',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': 'bond0',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			}
		]
