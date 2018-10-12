import json
from textwrap import dedent


class TestAddGroup:
	def test_no_args(self, host):
		result = host.run('stack add group')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" argument is required
			{group}
		''')

	def test_multiple_args(self, host):
		result = host.run('stack add group test test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" argument must be unique
			{group}
		''')

	def test_single_arg(self, host):
		# Add the group
		result = host.run('stack add group test')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list group test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"group": "test",
				"hosts": ""
			}
		]

	def test_duplicate(self, host):
		# Add the group
		result = host.run('stack add group test')
		assert result.rc == 0

		# Add the group again
		result = host.run('stack add group test')
		assert result.rc == 255
		assert result.stderr == 'error - "test" group already exists\n'
