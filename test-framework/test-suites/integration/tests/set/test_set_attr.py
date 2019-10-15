import json
from textwrap import dedent


class TestSetAttr:
	def test_invalid_scope(self, host):
		result = host.run('stack set attr attr=test value=True scope=foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "scope" parameter is not valid
			{attr=string} {value=string} [shadow=boolean]
		''')

	def test_scope_no_args(self, host):
		result = host.run('stack set attr attr=test value=True scope=host')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - argument is required
			{attr=string} {value=string} [shadow=boolean]
		''')

	def test_invalid_attr(self, host):
		result = host.run('stack set attr attr=test* value=True')
		assert result.rc == 255
		assert result.stderr == 'error - invalid attr name "test*"\n'

	def test_existing(self, host):
		# Add a test attr
		result = host.run('stack set attr attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list attr attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'scope': 'global',
			'type': 'var',
			'value': 'True'
		}]

		# Add the test attr again with a different value
		result = host.run('stack set attr attr=test value=False')
		assert result.rc == 0

		# Make sure it got overwritten
		result = host.run('stack list attr attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'scope': 'global',
			'type': 'var',
			'value': 'False'
		}]

	def test_shadow_attr(self, host):
		# Add a test attr
		result = host.run('stack set attr attr=test value=True shadow=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list attr attr=test shadow=True output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'scope': 'global',
			'type': 'shadow',
			'value': 'True'
		}]

		# And that it isn't shown with shadow=False
		result = host.run('stack list attr attr=test shadow=False output-format=json')
		assert result.rc == 0
		assert result.stdout == ""
