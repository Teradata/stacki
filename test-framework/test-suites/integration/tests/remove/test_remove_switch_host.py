import json
from textwrap import dedent


class TestRemoveSwitchHost:
	def test_no_args(self, host):
		result = host.run('stack remove switch host')
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

		# List the switch hosts to make sure it was added
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

		# Now remove the backend from the switch
		result = host.run('stack remove switch host switch-0-0 host=backend-0-0 interface=eth0 port=1')
		assert result.rc == 0

		# Make sure it's gone
		result = host.run('stack list switch host')
		assert result.rc == 0
		assert result.stdout == ''
