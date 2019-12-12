import json
from textwrap import dedent


class TestSwapHostInterface:
	def test_no_hosts(self, host):
		result = host.run('stack swap host interface')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {interfaces=string} [sync-config=boolean]
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack swap host interface a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {interfaces=string} [sync-config=boolean]
		''')

	def test_no_parameters(self, host):
		result = host.run('stack swap host interface frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "interfaces" parameter is required
			{host ...} {interfaces=string} [sync-config=boolean]
		''')

	def test_one_interface(self, host):
		result = host.run('stack swap host interface frontend-0-0 interfaces=eth0')
		assert result.rc == 255
		assert result.stderr == 'error - must supply exactly two interfaces\n'

	def test_three_interfaces(self, host):
		result = host.run('stack swap host interface frontend-0-0 interfaces=eth0,eth1,eth2')
		assert result.rc == 255
		assert result.stderr == 'error - must supply exactly two interfaces\n'

	def test_missing_interface(self, host):
		result = host.run('stack swap host interface frontend-0-0 interfaces=eth0,eth4')
		assert result.rc == 255
		assert result.stderr == 'error - one or more of the interfaces are missing\n'

	def test_minimal_parameters(self, host, add_host, revert_etc):
		# Add two minimal interfaces
		result = host.run('stack add host interface backend-0-0 mac=00:00:00:00:00:00 interface=eth0')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 mac=11:11:11:11:11:11 interface=eth1')
		assert result.rc == 0

		# Swap them
		result = host.run('stack swap host interface backend-0-0 interfaces=eth0,eth1 sync-config=no')
		assert result.rc == 0

		# Make sure they got swapped
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth0',
				'ip': None,
				'mac': '00:00:00:00:00:00',
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			},
			{
				'channel': None,
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': None,
				'mac': '11:11:11:11:11:11',
				'module': None,
				'name': None,
				'network': None,
				'options': None,
				'vlan': None
			}
		]

	def test_all_parameters(self, host, add_host, add_network, revert_etc):
		# Add two interfaces with all the fixins
		result = host.run(
			'stack add host interface backend-0-0 interface=eth1 '
			'mac=11:11:11:11:11:11 network=private ip=192.0.2.1 '
			'module=module_1 name=name_1 vlan=1 default=true '
			'options=options_1 channel=1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host interface backend-0-0 interface=eth2 '
			'mac=22:22:22:22:22:22 network=test ip=192.0.2.2 '
			'module=module_2 name=name_2 vlan=2 default=false '
			'options=options_2 channel=2'
		)
		assert result.rc == 0

		# Swap them
		result = host.run('stack swap host interface backend-0-0 interfaces=eth1,eth2 sync-config=no')
		assert result.rc == 0

		# Make sure they got swapped
		result = host.run('stack list host interface backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'channel': '2',
				'default': None,
				'host': 'backend-0-0',
				'interface': 'eth1',
				'ip': '192.0.2.2',
				'mac': '11:11:11:11:11:11',
				'module': 'module_1',
				'name': 'name_2',
				'network': 'test',
				'options': 'options_1',
				'vlan': 2
			},
			{
				'channel': '1',
				'default': True,
				'host': 'backend-0-0',
				'interface': 'eth2',
				'ip': '192.0.2.1',
				'mac': '22:22:22:22:22:22',
				'module': 'module_2',
				'name': 'name_1',
				'network': 'private',
				'options': 'options_2',
				'vlan': 1
			}
		]
