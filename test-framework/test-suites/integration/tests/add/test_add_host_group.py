import json
from textwrap import dedent


class TestAddHostGroup:
	def test_add_host_group_no_hosts(self, host):
		result = host.run('stack add host group')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {group=string}
		''')
	
	def test_add_host_group_no_matching_hosts(self, host):
		result = host.run('stack add host group a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {group=string}
		''')
	
	def test_add_host_group_no_group(self, host):
		result = host.run('stack add host group frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" parameter is required
			{host ...} {group=string}
		''')
	
	def test_add_host_group_invalid_group(self, host):
		result = host.run('stack add host group frontend-0-0 group=test')
		assert result.rc == 255
		assert result.stderr == 'error - group test does not exist\n'
	
	def test_add_host_group(self, host):
		# Create a few groups
		result = host.run('stack add group test')
		assert result.rc == 0
		
		result = host.run('stack add group coolkids')
		assert result.rc == 0

		# Add our host to the test group
		result = host.run('stack add host group frontend-0-0 group=test')
		assert result.rc == 0
		
		# List out the groups and make sure we are in test, and not in coolkids
		result = host.run('stack list group output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'group': 'coolkids',
				'hosts': ''
			},
			{
				'group': 'test',
				'hosts': 'frontend-0-0'
			}
		]
	
	def test_add_host_group_already_in_group(self, host):
		# Create a test group
		result = host.run('stack add group test')
		assert result.rc == 0

		# Add our host to the test group
		result = host.run('stack add host group frontend-0-0 group=test')
		assert result.rc == 0

		# Add our host to the test group again
		result = host.run('stack add host group frontend-0-0 group=test')
		assert result.rc == 255
		assert result.stderr == 'error - frontend-0-0 already member of test\n'
	