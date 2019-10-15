import json
from textwrap import dedent


class TestSetHostAttr:
	def test_no_args(self, host):
		result = host.run('stack set host attr attr=test value=True')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {attr=string} {value=string} [shadow=boolean]
		''')

	def test_invalid_attr(self, host, add_host):
		result = host.run('stack set host attr backend-0-0 attr=test* value=True')
		assert result.rc == 255
		assert result.stderr == 'error - invalid attr name "test*"\n'

	def test_existing(self, host, add_host):
		# Add a test attr
		result = host.run('stack set host attr backend-0-0 attr=test value=True')
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

		# Add the test attr again with a different value
		result = host.run('stack set host attr backend-0-0 attr=test value=False')
		assert result.rc == 0

		# Make sure it got overwritten
		result = host.run('stack list host attr backend-0-0 attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'var',
			'value': 'False'
		}]

	def test_shadow_attr(self, host, add_host):
		# Add a test attr
		result = host.run('stack set host attr backend-0-0 attr=test value=True shadow=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list host attr backend-0-0 attr=test shadow=True output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'shadow',
			'value': 'True'
		}]

		# And that it isn't shown with shadow=False
		result = host.run('stack list host attr backend-0-0 attr=test shadow=False output-format=json')
		assert result.rc == 0
		assert result.stdout == ""
