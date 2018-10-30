import json
from textwrap import dedent


class TestRemoveApplianceRoute:
	def test_no_args(self, host):
		result = host.run('stack remove appliance route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance} {address=string}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove appliance route test address=127.0.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			{appliance} {address=string}
		''')

	def test_no_address(self, host, add_appliance):
		result = host.run('stack remove appliance route test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{appliance} {address=string}
		''')

	def test_one_arg(self, host, add_appliance):
		# Add a couple appliance routes
		result = host.run('stack add appliance route test address=192.168.0.2 gateway=private')
		assert result.rc == 0

		result = host.run('stack add appliance route test address=192.168.0.3 gateway=private')
		assert result.rc == 0

		# Confirm they are there
		result = host.run('stack list appliance route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "test",
				"network": "192.168.0.2",
				"netmask": "255.255.255.255",
				"gateway": "",
				"subnet": "private",
				"interface": None
			},
			{
				"appliance": "test",
				"network": "192.168.0.3",
				"netmask": "255.255.255.255",
				"gateway": "",
				"subnet": "private",
				"interface": None
			}
		]

		# Now remove the first appliace route added
		result = host.run('stack remove appliance route test address=192.168.0.2')
		assert result.rc == 0

		# Make sure only one route was removed
		result = host.run('stack list appliance route test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"appliance": "test",
				"network": "192.168.0.3",
				"netmask": "255.255.255.255",
				"gateway": "",
				"subnet": "private",
				"interface": None
			}
		]

	def test_multiple_args(self, host, add_appliance):
		# Add a couple appliance routes to the "test" appliance
		result = host.run('stack add appliance route test address=192.168.0.2 gateway=private')
		assert result.rc == 0

		result = host.run('stack add appliance route test address=192.168.0.3 gateway=private')
		assert result.rc == 0

		# Add a second test appliance
		add_appliance('foo')

		# Add a couple appliance routes to the "foo" appliance
		result = host.run('stack add appliance route foo address=192.168.0.4 gateway=private')
		assert result.rc == 0

		result = host.run('stack add appliance route foo address=192.168.0.5 gateway=private')
		assert result.rc == 0

		# Confirm all our routes are there
		result = host.run('stack list appliance route test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'test',
				'gateway': '',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'subnet': 'private'
			},
			{
				'appliance': 'test',
				'gateway': '',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.3',
				'subnet': 'private'
			},
			{
				'appliance': 'foo',
				'gateway': '',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.4',
				'subnet': 'private'
			},
			{
				'appliance': 'foo',
				'gateway': '',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.5',
				'subnet': 'private'
			}
		]

		# Now remove the second route added to "test" appliance
		result = host.run('stack remove appliance route test address=192.168.0.3')
		assert result.rc == 0

		# And the first added to "foo" appliance
		result = host.run('stack remove appliance route foo address=192.168.0.4')
		assert result.rc == 0

		# Make sure only the expected routes were removed
		result = host.run('stack list appliance route test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'test',
				'gateway': '',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.2',
				'subnet': 'private'
			},
			{
				'appliance': 'foo',
				'gateway': '',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '192.168.0.5',
				'subnet': 'private'
			}
		]
