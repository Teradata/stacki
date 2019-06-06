import json
from textwrap import dedent


class TestAddHostAttr:
	def test_no_args(self, host):
		result = host.run('stack add host attr attr=test value=True')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {attr=string} {value=string} [shadow=boolean]
		''')

	def test_existing(self, host, add_host):
		# Add a test attr
		result = host.run('stack add host attr backend-0-0 attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list host attr backend-0-0 attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'var',
			'value': 'True'
		}]

		# Add the test attr again, which should fail
		result = host.run('stack add host attr backend-0-0 attr=test value=False')
		assert result.rc == 255
		assert result.stderr == 'error - attr "test" already exists\n'
