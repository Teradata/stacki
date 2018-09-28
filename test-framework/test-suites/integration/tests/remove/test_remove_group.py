import json
from textwrap import dedent


class TestRemoveGroup:
	def test_remove_group_no_args(self, host):
		result = host.run('stack remove group')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" argument is required
			{group}
		''')

	def test_remove_group_invalid(self, host):
		result = host.run('stack remove group test')
		assert result.rc == 255
		assert result.stderr == 'error - group test does not exist\n'

	def test_remove_group_multiple_args(self, host):
		result = host.run('stack remove group test test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" argument must be unique
			{group}
		''')

	def test_remove_group_in_use(self, host, add_host):
		# Add the group
		result = host.run('stack add group test')
		assert result.rc == 0

		# Add our test host to the group
		result = host.run('stack add host group backend-0-0 group=test')
		assert result.rc == 0

		# Check that it is there now
		result = host.run('stack list group test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				"group": "test",
				"hosts": "backend-0-0"
			}
		]

		# Now try to remove it, which should fail
		result = host.run('stack remove group test')
		assert result.rc == 255
		assert result.stderr == 'error - group test is in use\n'

	def test_remove_group(self, host, add_host):
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

		# Now remove it
		result = host.run('stack remove group test')
		assert result.rc == 0

		# Check that it is gone
		result = host.run('stack list group test')
		assert result.rc == 0
		assert result.stdout == ''
