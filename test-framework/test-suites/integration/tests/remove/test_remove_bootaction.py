import json
from textwrap import dedent


class TestRemoveBootaction:
	def test_remove_bootaction_no_args(self, host):
		result = host.run('stack remove bootaction')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" argument is required
			{action} [os=string] [type=string]
		''')

	def test_remove_bootaction_multiple_args(self, host):
		result = host.run('stack remove bootaction test foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" argument must be unique
			{action} [os=string] [type=string]
		''')

	def test_remove_bootaction_no_type(self, host):
		result = host.run('stack remove bootaction test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "type" parameter is required
			{action} [os=string] [type=string]
		''')

	def test_remove_bootaction_invalid_action(self, host):
		result = host.run('stack remove bootaction test type=os')
		assert result.rc == 255
		assert result.stderr == 'error - action/type/os "test/os/" does not exists\n'

	def test_remove_bootaction_default_os(self, host, host_os):
		# Add an install bootaction that will get the default os
		result = host.run('stack add bootaction test type=install kernel=""')
		assert result.rc == 0

		# Make sure the action got added
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'test',
				'kernel': None,
				'os': host_os,
				'ramdisk': None,
				'type': 'install'
			}
		]

		# Now remove it
		result = host.run('stack remove bootaction test type=install')
		assert result.rc == 0

		# Make sure it's gone
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert result.stdout == ''

	def test_remove_bootaction_with_os(self, host):
		# Add an os bootaction with a specified os
		result = host.run('stack add bootaction test type=os os=ubuntu kernel=""')
		assert result.rc == 0

		# Make sure the action got added
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'test',
				'kernel': None,
				'os': 'ubuntu',
				'ramdisk': None,
				'type': 'os'
			}
		]

		# Now remove it
		result = host.run('stack remove bootaction test type=os os=ubuntu')
		assert result.rc == 0

		# Make sure it's gone
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert result.stdout == ''

	def test_remove_bootaction_os_is_null(self, host):
		# Add an os bootaction with a null os
		result = host.run('stack add bootaction test type=os kernel=""')
		assert result.rc == 0

		# Make sure the action got added
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'test',
				'kernel': None,
				'os': None,
				'ramdisk': None,
				'type': 'os'
			}
		]

		# Now remove it
		result = host.run('stack remove bootaction test type=os')
		assert result.rc == 0

		# Make sure it's gone
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert result.stdout == ''
