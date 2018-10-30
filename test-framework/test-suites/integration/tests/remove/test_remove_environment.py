import json
from textwrap import dedent


class TestRemoveEnvironment:
	def test_no_args(self, host):
		result = host.run('stack remove environment')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove environment test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid environment
			{environment ...}
		''')

	def test_in_use(self, host, add_host, add_environment):
		# Add our test backend to the test environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Try to remove the test environment, which is in use
		result = host.run('stack remove environment test')
		assert result.rc == 255
		assert result.stderr == 'error - environment test in use\n'

	def test_one_arg(self, host, add_environment):
		# Add some environment scoped data to exercise the plugins
		result = host.run('stack add environment attr test attr=test value=true')
		assert result.rc == 0

		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run('stack add environment route test address=192.168.0.2 gateway=private')
		assert result.rc == 0

		# Remove our test environment
		result = host.run('stack remove environment test')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list environment test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid environment
			[environment ...]
		''')

	def test_multiple_args(self, host, add_environment):
		# Add a second test environment
		add_environment('foo')

		# Add some environment scoped data to exercise the plugins
		result = host.run('stack add environment attr foo attr=test value=true')
		assert result.rc == 0

		result = host.run(
			'stack add environment firewall foo service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run('stack add environment route foo address=192.168.0.2 gateway=private')
		assert result.rc == 0

		# Remove our test environments
		result = host.run('stack remove environment test foo')
		assert result.rc == 0

		# Make sure test environment is gone
		result = host.run('stack list environment test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid environment
			[environment ...]
		''')

		# Make sure foo environment is gone
		result = host.run('stack list environment foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid environment
			[environment ...]
		''')
