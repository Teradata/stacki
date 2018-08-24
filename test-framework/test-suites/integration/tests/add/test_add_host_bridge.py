import json
from textwrap import dedent

import pytest


@pytest.mark.usefixtures("add_host_with_interface")
class TestAddHostBridge:
	def test_add_host_bridge_no_hosts(self, host):
		result = host.run('stack add host bridge')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [interface=string] [name=string] [network=string]
		''')
	
	def test_add_host_bridge_no_matching_hosts(self, host):
		result = host.run('stack add host bridge a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [interface=string] [name=string] [network=string]
		''')
	
	def test_add_host_bridge_no_name(self, host):
		result = host.run('stack add host bridge backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "name" parameter is required
			{host} [interface=string] [name=string] [network=string]
		''')
	
	def test_add_host_bridge_no_interface_or_network(self, host):
		result = host.run('stack add host bridge backend-0-0 name=br0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "network" parameter is required
			{host} [interface=string] [name=string] [network=string]
		''')
	
	def test_add_host_bridge_invalid_interface(self, host):
		result = host.run('stack add host bridge backend-0-0 name=br0 interface=test')
		assert result.rc == 255
		assert result.stderr == 'error - Could not find interface test configured on host backend-0-0\n'
	
	def test_add_host_bridge_invalid_network(self, host):
		result = host.run('stack add host bridge backend-0-0 name=br0 network=test')
		assert result.rc == 255
		assert result.stderr == 'error - Could not find network test on host backend-0-0\n'
	
	def test_add_host_bridge_only_interface(self, host):
		# Set the network for the eth0 interface on backend-0-0
		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		# Add the bridge interface
		result = host.run('stack add host bridge backend-0-0 name=br0 interface=eth0')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'br0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'None',
				'network': 'private',
				'options': 'bridge',
				'vlan': None
			},
			{
				'channel': 'br0',
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
	
	def test_add_host_bridge_only_network(self, host):
		# Set the network for the eth0 interface on backend-0-0
		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=private')
		assert result.rc == 0
		
		# Add the bridge interface
		result = host.run('stack add host bridge backend-0-0 name=br0 network=private')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'br0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'None',
				'network': 'private',
				'options': 'bridge',
				'vlan': None
			},
			{
				'channel': 'br0',
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
	
	def test_add_host_bridge_interface_and_network(self, host):
		# Set the network for the eth0 interface on backend-0-0
		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=private')
		assert result.rc == 0
		
		# Add the bridge interface
		result = host.run('stack add host bridge backend-0-0 name=br0 interface=eth0 network=private')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'br0',
				'ip': None,
				'mac': None,
				'module': None,
				'name': 'None',
				'network': 'private',
				'options': 'bridge',
				'vlan': None
			},
			{
				'channel': 'br0',
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
	
	def test_add_host_bridge_default_with_ip(self, host):
		# Set the network for the eth0 interface on backend-0-0
		result = host.run('stack set host interface network backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		# Set an ip address for the eth0 interface on backend-0-0
		result = host.run('stack set host interface ip backend-0-0 interface=eth0 ip=192.168.0.1')
		assert result.rc == 0
		
		# Make the eth0 interface on backend-0-0 the default
		result = host.run('stack set host interface default backend-0-0 interface=eth0 default=true')
		assert result.rc == 0
		
		# Add the bridge interface
		result = host.run('stack add host bridge backend-0-0 name=br0 interface=eth0')
		assert result.rc == 0

		# Check the interface is in the database now
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': True,
				'host': 'backend-0-0',
				'interface': 'br0',
				'ip': '192.168.0.1',
				'mac': None,
				'module': None,
				'name': 'None',
				'network': 'private',
				'options': 'bridge',
				'vlan': None
			},
			{
				'channel': 'br0',
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
