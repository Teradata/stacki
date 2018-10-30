import json
from textwrap import dedent


class TestRemoveOSRoute:
	def test_no_args(self, host):
		result = host.run('stack remove os route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {address=string}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove os route test address=192.168.0.1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid OS
			{os ...} {address=string}
		''')

	def test_no_address(self, host):
		result = host.run('stack remove os route sles')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{os ...} {address=string}
		''')

	def test_one_arg(self, host):
		# Add an os route
		result = host.run(
			'stack add os route sles address=127.0.0.3 gateway=127.0.0.3'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list os route sles output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'os': 'sles',
			'network': '127.0.0.3',
			'netmask': '255.255.255.255',
			'gateway': '127.0.0.3',
			'subnet': None,
			'interface': None
		}]

		# Delete the route
		result = host.run('stack remove os route sles address=127.0.0.3')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list os route sles')
		assert result.rc == 0
		assert result.stdout == ''

	def test_multiple_args(self, host):
		# Add an os route to sles
		result = host.run(
			'stack add os route sles address=127.0.0.3 gateway=127.0.0.3'
		)
		assert result.rc == 0

		# Add it to redhat as well
		result = host.run(
			'stack add os route redhat address=127.0.0.3 gateway=127.0.0.3'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list os route sles redhat output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'os': 'redhat',
				'network': '127.0.0.3',
				'netmask': '255.255.255.255',
				'gateway': '127.0.0.3',
				'subnet': None,
				'interface': None
			},
			{
				'os': 'sles',
				'network': '127.0.0.3',
				'netmask': '255.255.255.255',
				'gateway': '127.0.0.3',
				'subnet': None,
				'interface': None
			}
		]

		# Delete the route from both OSes
		result = host.run('stack remove os route sles redhat address=127.0.0.3')
		assert result.rc == 0

		# Make sure they are gone now
		result = host.run('stack list os route sles')
		assert result.rc == 0
		assert result.stdout == ''
