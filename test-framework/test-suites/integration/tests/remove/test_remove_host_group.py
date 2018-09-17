import json
from textwrap import dedent


class TestRemoveHostGroup:
	def test_remove_host_group_invalid_host(self, host):
		result = host.run('stack remove host group test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_remove_host_group_no_args(self, host):
		result = host.run('stack remove host group')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {group=string}
		''')

	def test_remove_host_group_no_host_matches(self, host):
		result = host.run('stack remove host group a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {group=string}
		''')

	def test_remove_host_group_no_group(self, host):
		result = host.run('stack remove host group frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" parameter is required
			{host ...} {group=string}
		''')

	def test_remove_host_group_host_not_in_group(self, host, add_group):
		result = host.run('stack remove host group frontend-0-0 group=test')
		assert result.rc == 255
		assert result.stderr == 'error - frontend-0-0 is not a member of test\n'

	def test_remove_host_group_single_arg(self, host, add_group):
		# Add our host to the test group
		result = host.run('stack add host group frontend-0-0 group=test')
		assert result.rc == 0

		# Confirm we are in the group now
		result = host.run('stack list host group frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'groups': 'test'
			}
		]

		# Now remove our host from the group
		result = host.run('stack remove host group frontend-0-0 group=test')
		assert result.rc == 0

		# Confirm it is removed
		result = host.run('stack list host group frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'groups': ''
			}
		]

	def test_remove_host_group_multiple_args(self, host, add_host, add_group):
		# Add the hosts to the test group
		result = host.run('stack add host group frontend-0-0 backend-0-0 group=test')
		assert result.rc == 0

		# Confirm we are in the group now
		result = host.run('stack list host group frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'groups': 'test'
			},
			{
				'host': 'backend-0-0',
				'groups': 'test'
			}
		]

		# Now remove our hosts from the group
		result = host.run('stack remove host group frontend-0-0 backend-0-0 group=test')
		assert result.rc == 0

		# Confirm it is removed
		result = host.run('stack list host group frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'groups': ''
			},
			{
				'host': 'backend-0-0',
				'groups': ''
			}
		]
