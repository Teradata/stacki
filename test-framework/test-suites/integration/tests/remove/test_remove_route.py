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
		assert '127.0.0.3' in {
			route['network'] for route in json.loads(result.stdout)
		}

		# Delete the route
		result = host.run('stack remove route address=127.0.0.3')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list route output-format=json')
		assert result.rc == 0
		assert '127.0.0.3' not in {
			route['network'] for route in json.loads(result.stdout)
		}
