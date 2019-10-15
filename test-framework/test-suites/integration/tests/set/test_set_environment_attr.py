import json
from textwrap import dedent


class TestSetEnvironmentAttr:
	def test_no_args(self, host):
		result = host.run('stack set environment attr attr=test value=True')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {attr=string} {value=string} [shadow=boolean]
		''')

	def test_existing(self, host, add_environment):
		# Add a test attr
		result = host.run('stack set environment attr test attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list environment attr test attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'environment': 'test',
			'scope': 'environment',
			'type': 'var',
			'value': 'True'
		}]

		# Add the test attr again with a different value
		result = host.run('stack set environment attr test attr=test value=False')
		assert result.rc == 0

		# Make sure it got overwritten
		result = host.run('stack list environment attr test attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'environment': 'test',
			'scope': 'environment',
			'type': 'var',
			'value': 'False'
		}]
