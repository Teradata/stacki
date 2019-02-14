import json


class TestListSwitchStatus:
	def test_x1052(self, host, add_host, inject_code, test_file):
		# Add an interface to our backend
		result = host.run('stack add host interface backend-0-0 mac=00:00:00:00:00:00 interface=eth0 network=private')
		assert result.rc == 0

		# Add a second backend with an interface
		add_host('backend-0-1', '0', '1', 'backend')

		result = host.run('stack add host interface backend-0-1 interface=eth1 network=private')
		assert result.rc == 0

		# Add our x1052 switch
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Add our backends to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		result = host.run('stack add switch host switch-0-0 host=backend-0-1 interface=eth1 port=2')
		assert result.rc == 0

		# Inject our Mock code to replace the communication with actual hardware
		with inject_code(test_file('list/mock_switch_status_test_x1052.py')):
			# List the switch status
			result = host.run('stack list switch status switch-0-0 output-format=json')

		# Make sure the output is what we expect
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'backend-0-0',
				'interface': 'eth0',
				'mac': '00:00:00:00:00:00',
				'port': '1',
				'speed': '--',
				'state': 'Down',
				'switch': 'switch-0-0',
				'vlan': None
			},
			{
				'host': 'backend-0-1',
				'interface': 'eth1',
				'mac': None,
				'port': '2',
				'speed': '1000',
				'state': 'Up',
				'switch': 'switch-0-0',
				'vlan': None
			},
			{
				'host': '',
				'interface': '',
				'mac': '',
				'port': '3',
				'speed': '1000',
				'state': 'Up',
				'switch': 'switch-0-0',
				'vlan': ''
			}
		]

	def test_x1052_not_same_network(self, host, add_network):
		# Add our x1052 switch on the wrong network
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=test ip=127.0.0.1')
		assert result.rc == 0

		# Try to list the switch macs, which should error out
		result = host.run('stack list switch status output-format=json')
		assert result.rc == 255
		assert result.stderr == 'error - "switch-0-0" and the frontend do not share a network\n'

	def test_x1052_switch_exception(self, host, inject_code, test_file):
		# Add our x1052 switch
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Inject our Mock code to throw an execption when trying to connect
		with inject_code(test_file('list/mock_test_x1052_switch_exception.py')):
			result = host.run('stack list switch status output-format=json')

		# It should have failed
		assert result.rc == 255
		assert result.stderr == "error - Couldn't connect to the switch\n"

	def test_x1052_other_exception(self, host, inject_code, test_file):
		# Add our x1052 switch
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Inject our Mock code to throw an execption when trying to open a file
		with inject_code(test_file('list/mock_test_x1052_other_exception.py')):
			result = host.run('stack list switch status output-format=json')

		# It should have failed
		assert result.rc == 255
		assert result.stderr == "error - There was an error getting the status of the switch.\n"
