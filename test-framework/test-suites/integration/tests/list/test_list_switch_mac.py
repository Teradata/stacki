import json


class TestListSwitchMac:
	def test_x1052(self, host, add_host, inject_code):
		# Add an interface with a known MAC to our backend
		result = host.run('stack add host interface backend-0-0 mac=00:00:00:00:00:00 ip=127.0.0.2 interface=eth0 network=private')
		assert result.rc == 0

		# Add our x1052 switch
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Inject our Mock code to replace the communication with actual hardware
		with inject_code('/export/test-files/list/mock_switch_mac_test_x1052.py'):
			# List the switch hosts
			result = host.run('stack list switch mac pinghosts=true output-format=json')

		# Make sure the output is what we expect
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'interface': 'eth0',
			'mac': '00:00:00:00:00:00',
			'port': '10',
			'switch': 'switch-0-0',
			'vlan': '1'
		}]

	def test_x1052_not_same_network(self, host, add_network):
		# Add our x1052 switch on the wrong network
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=test ip=127.0.0.1')
		assert result.rc == 0

		# Try to list the switch macs, which should error out
		result = host.run('stack list switch mac output-format=json')
		assert result.rc == 255
		assert result.stderr == 'error - "switch-0-0" and the frontend do not share a network\n'

	def test_x1052_switch_exception(self, host, inject_code):
		# Add our x1052 switch
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Inject our Mock code to throw an execption when trying to connect
		with inject_code('/export/test-files/list/mock_test_x1052_switch_exception.py'):
			result = host.run('stack list switch mac output-format=json')

		# It should have failed
		assert result.rc == 255
		assert result.stderr == "error - Couldn't connect to the switch\n"

	def test_x1052_other_exception(self, host, inject_code):
		# Add our x1052 switch
		result = host.run('stack add host switch-0-0')
		assert result.rc == 0

		result = host.run('stack set host attr switch-0-0 attr=component.model value=x1052')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Inject our Mock code to throw an execption when trying to open a file
		with inject_code('/export/test-files/list/mock_test_x1052_other_exception.py'):
			result = host.run('stack list switch mac output-format=json')

		# It should have failed
		assert result.rc == 255
		assert result.stderr == "error - There was an error getting the mac address table\n"
