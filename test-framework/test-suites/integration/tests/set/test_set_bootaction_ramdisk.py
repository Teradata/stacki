import json
from textwrap import dedent


class TestSetBootactionRamdisk:
	def test_no_args(self, host):
		result = host.run('stack set bootaction ramdisk')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" argument is required
			{action} {ramdisk=string} [os=string] [type=string]
		''')

	def test_multiple_args(self, host):
		result = host.run('stack set bootaction ramdisk test foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" argument must be unique
			{action} {ramdisk=string} [os=string] [type=string]
		''')

	def test_invalid_action(self, host):
		result = host.run('stack set bootaction ramdisk test type=os ramdisk=test')
		assert result.rc == 255
		assert result.stderr == 'error - action "test" does not exist\n'

	def test_no_type(self, host):
		result = host.run('stack set bootaction ramdisk memtest')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "type" parameter is required
			{action} {ramdisk=string} [os=string] [type=string]
		''')

	def test_invalid_type(self, host):
		result = host.run('stack set bootaction ramdisk memtest type=foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "type" parameter must be "os" or "install"
			{action} {ramdisk=string} [os=string] [type=string]
		''')

	def test_no_ramdisk_parameter(self, host):
		result = host.run('stack set bootaction ramdisk memtest type=os')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "ramdisk" parameter is required
			{action} {ramdisk=string} [os=string] [type=string]
		''')

	def test_with_os(self, host):
		# Add a test bootaction with an OS
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

		# Set the bootaction ramdisk with a specified os
		result = host.run(f'stack set bootaction ramdisk test type=os os=ubuntu ramdisk="test_ramdisk"')
		assert result.rc == 0

		# Make sure the kernel got set
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'test',
				'kernel': None,
				'os': 'ubuntu',
				'ramdisk': 'test_ramdisk',
				'type': 'os'
			}
		]

	def test_os_is_null(self, host):
		# Set the bootaction kernel with a null os
		result = host.run('stack set bootaction ramdisk memtest type=os ramdisk="test_ramdisk"')
		assert result.rc == 0

		# Make sure the action got added
		result = host.run('stack list bootaction memtest output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'memtest',
				'kernel': 'kernel memtest',
				'os': None,
				'ramdisk': 'test_ramdisk',
				'type': 'os'
			}
		]
