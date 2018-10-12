import json
from textwrap import dedent


class TestSetBootactionKernel:
	def test_no_args(self, host):
		result = host.run('stack set bootaction kernel')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" argument is required
			{action} {kernel=string} [os=string] [type=string]
		''')

	def test_multiple_args(self, host):
		result = host.run('stack set bootaction kernel test foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" argument must be unique
			{action} {kernel=string} [os=string] [type=string]
		''')

	def test_invalid_action(self, host):
		result = host.run('stack set bootaction kernel test type=os kernel=test')
		assert result.rc == 255
		assert result.stderr == 'error - action "test" does not exist\n'

	def test_no_type(self, host):
		result = host.run('stack set bootaction kernel memtest')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "type" parameter is required
			{action} {kernel=string} [os=string] [type=string]
		''')

	def test_invalid_type(self, host):
		result = host.run('stack set bootaction kernel memtest type=foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "type" parameter must be "os" or "install"
			{action} {kernel=string} [os=string] [type=string]
		''')

	def test_no_kernel_parameter(self, host):
		result = host.run('stack set bootaction kernel memtest type=os')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "kernel" parameter is required
			{action} {kernel=string} [os=string] [type=string]
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

		# Set the bootaction kernel with a specified os
		result = host.run(f'stack set bootaction kernel test type=os os=ubuntu kernel="test_kernel"')
		assert result.rc == 0

		# Make sure the kernel got set
		result = host.run('stack list bootaction test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'test',
				'kernel': 'test_kernel',
				'os': 'ubuntu',
				'ramdisk': None,
				'type': 'os'
			}
		]

	def test_os_is_null(self, host):
		# Set the bootaction kernel with a null os
		result = host.run('stack set bootaction kernel memtest type=os kernel="test_kernel"')
		assert result.rc == 0

		# Make sure the action got added
		result = host.run('stack list bootaction memtest output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'args': None,
				'bootaction': 'memtest',
				'kernel': 'test_kernel',
				'os': None,
				'ramdisk': None,
				'type': 'os'
			}
		]
