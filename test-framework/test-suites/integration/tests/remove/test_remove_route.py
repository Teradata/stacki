import json
from textwrap import dedent


class TestRemoveRoute:
	def test_no_args(self, host):
		result = host.run('stack remove route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{address=string}
		''')

	def test_one_arg(self, host):
		# Add a global route
		result = host.run('stack add route address=127.0.0.3 gateway=127.0.0.3')
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list route output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '127.0.0.3',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '127.0.0.3',
				'subnet': None
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'subnet': 'private'
			}
		]

		# Delete the route
		result = host.run('stack remove route address=127.0.0.3')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list route output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'subnet': 'private'
			}
		]
