import json
from textwrap import dedent


class TestSetAccess:
	def test_no_args(self, host):
		result = host.run('stack set access')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "command" parameter is required
			{command=string} {group=string}
		''')

	def test_no_command(self, host):
		result = host.run('stack set access group=apache')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "command" parameter is required
			{command=string} {group=string}
		''')

	def test_no_group(self, host):
		result = host.run('stack set access command="*"')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "group" parameter is required
			{command=string} {group=string}
		''')

	def test_invalid_group(self, host):
		result = host.run('stack set access command="*" group=test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot find group test\n'

	def test_group_name(self, host):
		# Give all access to group 'adm'
		result = host.run('stack set access command="*" group=adm')
		assert result.rc == 0

		# Confirm it got added
		result = host.run('stack list access output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'command': '*',
				'group': 'root'
			},
			{
				'command': '*',
				'group': 'apache'
			},
			{
				'command': 'list*',
				'group': 'wheel'
			},
			{
				'command': 'list *',
				'group': 'nobody'
			},
			{
				'command': '*',
				'group': 'adm'
			}
		]

	def test_group_id(self, host):
		# Get the adm group id
		gid = host.group('adm').gid

		# Give all access to group 'adm'
		result = host.run(f'stack set access command="*" group={gid}')
		assert result.rc == 0

		# Confirm it got added
		result = host.run('stack list access output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'command': '*',
				'group': 'root'
			},
			{
				'command': '*',
				'group': 'apache'
			},
			{
				'command': 'list*',
				'group': 'wheel'
			},
			{
				'command': 'list *',
				'group': 'nobody'
			},
			{
				'command': '*',
				'group': 'adm'
			}
		]
