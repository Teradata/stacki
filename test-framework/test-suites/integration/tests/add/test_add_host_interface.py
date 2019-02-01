import json
from textwrap import dedent

import pytest


@pytest.mark.usefixtures("add_host")
class TestAddHostInterface:
	def test_no_hosts(self, host):
		result = host.run('stack add host interface')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [channel=string] [default=boolean] [interface=string] [ip=string] [mac=string] [module=string] [name=string] [network=string] [vlan=string]
		''')
	
	def test_no_matching_hosts(self, host):
		result = host.run('stack add host interface a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [channel=string] [default=boolean] [interface=string] [ip=string] [mac=string] [module=string] [name=string] [network=string] [vlan=string]
		''')
	
	def test_no_interface_or_mac(self, host):
		result = host.run('stack add host interface backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interface" or "mac" parameter is required
			{host} [channel=string] [default=boolean] [interface=string] [ip=string] [mac=string] [module=string] [name=string] [network=string] [vlan=string]
		''')

	def test_duplicate_interface(self, host):
		# Add the interface
		result = host.run('stack add host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add host interface backend-0-0 interface=eth0')
		assert result.rc == 255
		assert 'exists' in result.stderr

	def test_duplicate_mac(self, host):
		# Add the interface
		result = host.run('stack add host interface backend-0-0 interface=eth0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add host interface backend-0-0 interface=eth1 mac=00:11:22:33:44:55')
		assert result.rc == 255
		assert 'exists' in result.stderr

	def test_invalid_name(self, host):
		result = host.run('stack add host interface backend-0-0 interface=eth0 name=test.example.com')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "name" parameter must be a non-FQDN (base hostname)
			{host} [channel=string] [default=boolean] [interface=string] [ip=string] [mac=string] [module=string] [name=string] [network=string] [vlan=string]
		''')
	
	def test_invalid_network(self, host):
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=test')
		assert result.rc == 255
		assert result.stderr == 'error - network "test" does not exist\n'
	
	def test_invalid_vlan(self, host):
		result = host.run('stack add host interface backend-0-0 interface=eth0 vlan=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "vlan" parameter must be an integer
			{host} [channel=string] [default=boolean] [interface=string] [ip=string] [mac=string] [module=string] [name=string] [network=string] [vlan=string]
		''')
	
	def test_only_interface(self, host):
		# Add the interface
		result = host.run('stack add host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# Check all the data made it into the DB
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
	
	def test_only_mac(self, host):
		# Add the interface
		result = host.run('stack add host interface backend-0-0 mac=00:11:22:33:44:55')
		assert result.rc == 0

		# Check all the data made it into the DB
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
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
			}
		]

	def test_all_parameters(self, host):
		# Add the interface
		result = host.run(
			'stack add host interface backend-0-0 '
			'interface=eth0 mac=00:11:22:33:44:55 network=private '
			'ip=127.0.0.1 module=test_module name=test_name '
			'vlan=1 default=true options=test_options channel=1'
		)
		assert result.rc == 0

		# Check all the data made it into the DB
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': '1',
				'default': True,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': '127.0.0.1',
				'mac': '00:11:22:33:44:55',
				'module': 'test_module',
				'name': 'test_name',
				'network': 'private',
				'options': 'test_options',
				'vlan': 1
			}
		]
	
	def test_empty_parameters(self, host):
		# Add the interface
		result = host.run(
			'stack add host interface backend-0-0 '
			'interface=eth0 mac=00:11:22:33:44:55 '
			'network="" ip="" module="" name="" '
			'vlan="" default="" options="" channel=""'
		)
		assert result.rc == 0

		# Check all the data made it into the DB
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
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
			}
		]
	
	def test_NULL_parameters(self, host):
		# Add the interface
		result = host.run(
			'stack add host interface backend-0-0 '
			'interface=eth0 mac=00:11:22:33:44:55 '
			'ip=NULL module=NULL name=NULL vlan=0 channel=NULL'
		)
		assert result.rc == 0

		# Check all the data made it into the DB
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': None,
				'mac': '00:11:22:33:44:55',
				'module': None,
				'name': 'backend-0-0',
				'network': None,
				'options': None,
				'vlan': None
			}
		]

	def test_ip_auto_no_network(self, host):
		# Add the interface
		result = host.run(
			'stack add host interface backend-0-0 '
			'interface=eth0 ip=auto'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" parameter is required
			{host} [channel=string] [default=boolean] [interface=string] [ip=string] [mac=string] [module=string] [name=string] [network=string] [vlan=string]
		''')

	def test_ip_auto(self, host):
		# Add the interface
		result = host.run(
			'stack add host interface backend-0-0 '
			'interface=eth0 ip=auto network=private'
		)
		assert result.rc == 0

		# Check all the data made it into the DB
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': '192.168.0.1',
				'mac': None,
				'module': None,
				'name': None,
				'network': 'private',
				'options': None,
				'vlan': None
			}
		]


	def test_duplicate_default_interface(self, host):
		# Add a default host interface
		result = host.run('stack add host interface backend-0-0 interface=eth0 default=true')
		assert result.rc == 0

		# Check data
		result = host.run('stack list host interface backend-0-0 output-format=json')
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
			}
		]

		# Add a new default host inteface to the same host
		result = host.run('stack add host interface backend-0-0 interface=eth1 default=true')
		assert result.rc == 0

		# Check data for duplicate default interface for the same host
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
			},
			{
				'channel': None,
				'default': True,
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
