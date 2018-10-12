import json
from textwrap import dedent


class TestAddEnvironment:
	def test_no_args(self, host):
		result = host.run('stack add environment')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment}
		''')

	def test_multiple_args(self, host):
		result = host.run('stack add environment test test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument must be unique
			{environment}
		''')

	def test_single_arg(self, host):
		# Add the environment
		result = host.run('stack add environment test')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list environment test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"environment": "test"
			}
		]

	def test_duplicate(self, host):
		# Add the environment
		result = host.run('stack add environment test')
		assert result.rc == 0
		
		# Add the environment again
		result = host.run('stack add environment test')
		assert result.rc == 255
		assert result.stderr == 'error - environment "test" already exists\n'
