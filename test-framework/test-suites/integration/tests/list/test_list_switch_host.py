import json


class TestListSwitchHost:
	def test_no_args(self, host, add_host, add_switch):
		# Add interfaces to our switch and backend
		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		# Add our backend to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# List the switch hosts
		result = host.run('stack list switch host output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'interface': 'eth0',
			'mac': None,
			'port': 1,
			'switch': 'switch-0-0',
			'vlan': None
		}]

	def test_one_arg(self, host, add_host, add_switch):
		# Add interfaces to our switch and backend
		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		# Add our backend to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# List the switch hosts
		result = host.run('stack list switch host switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'interface': 'eth0',
			'mac': None,
			'port': 1,
			'switch': 'switch-0-0',
			'vlan': None
		}]

	def test_skip_interface(self, host, add_host, add_switch):
		# Add interfaces to our switch and backend
		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		# Add our backend to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# Now remove the backend interface, which should now get skipped
		result = host.run('stack remove host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# List the switch hosts
		result = host.run('stack list switch host switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout == ''
