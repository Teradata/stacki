import json
from textwrap import dedent


class TestSetSwitchHostPort:
	def test_no_args(self, host):
		result = host.run('stack set switch host port')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "switch" argument is required
			{switch} {host=string} {interface=string} {port=string}
		''')

	def test_one_arg(self, host, add_host, add_switch):
		# Add interfaces to our backend and switch
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface backend-0-0 interface=eth1 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Add our backend to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# Now set the host port to be 2
		result = host.run('stack set switch host port switch-0-0 host=backend-0-0 interface=eth0 port=2')
		assert result.rc == 0

		# List the switch hosts to make sure the update made it
		result = host.run('stack list switch host output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'interface': 'eth0',
			'mac': None,
			'port': 2,
			'switch': 'switch-0-0',
			'vlan': None
		}]

	def test_multiple_args(self, host, add_switch):
		# Add a second switch
		add_switch('switch-0-1', '0', '1', 'switch', 'fake', 'unrl')

		# Run our command with both
		result = host.run('stack set switch host port switch-0-0 switch-0-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "switch" argument must be unique
			{switch} {host=string} {interface=string} {port=string}
		''')

	def test_no_hosts(self, host, add_switch):
		result = host.run('stack set switch host port switch-0-0 host=a:test interface=eth0 port=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" parameter is required
			{switch} {host=string} {interface=string} {port=string}
		''')

	def test_multiple_hosts(self, host, add_host, add_switch):
		# Add a second backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Run the command with a hosts parameter that will resolve to both
		result = host.run('stack set switch host port switch-0-0 host=a:backend interface=eth0 port=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" parameter must be unique
			{switch} {host=string} {interface=string} {port=string}
		''')

	def test_invalid_port(self, host, add_host, add_switch):
		result = host.run('stack set switch host port switch-0-0 host=backend-0-0 interface=eth0 port=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "port" parameter must be an integer
			{switch} {host=string} {interface=string} {port=string}
		''')

	def test_bad_host_interface_combo(self, host, add_host, add_switch):
		# Add interfaces to our backend and switch
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Add our backend to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# Now run our set command with the a bad interface
		result = host.run('stack set switch host port switch-0-0 host=backend-0-0 interface=eth1 port=2')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host/interface" argument "backend-0-0/eth1" not found
			{switch} {host=string} {interface=string} {port=string}
		''')

	def test_missing_host_interface(self, host, add_host, add_switch):
		# Add interfaces to our backend and switch
		result = host.run('stack add host interface backend-0-0 interface=eth0 network=private')
		assert result.rc == 0

		result = host.run('stack add host interface switch-0-0 interface=eth0 network=private ip=127.0.0.1')
		assert result.rc == 0

		# Add our backend to the test switch
		result = host.run('stack add switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# Now remove the interface from our host, trying to trick the command
		result = host.run('stack remove host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# Now run our set command with the missing host interface
		result = host.run('stack set switch host port switch-0-0 host=backend-0-0 interface=eth0 port=2')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host/interface" argument "backend-0-0/eth0" not found
			{switch} {host=string} {interface=string} {port=string}
		''')
