import json
from textwrap import dedent


class TestRemoveOS:
	def test_remove_os_no_args(self, host):
		result = host.run('stack remove os')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...}
		''')

	def test_remove_os_invalid(self, host):
		result = host.run('stack remove os test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid OS
			{os ...}
		''')

	def test_remove_os_one_arg(self, host):
		# Add some child data to the OS scope, to exercise the plugins
		result = host.run('stack add os attr ubuntu attr=test value=True')
		assert result.rc == 0

		result = host.run(
			'stack add os firewall ubuntu service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run(
			'stack add os route ubuntu address=127.0.0.3 gateway=127.0.0.3'
		)
		assert result.rc == 0

		# Now delete the OS
		result = host.run('stack remove os ubuntu')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list os ubuntu')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "ubuntu" argument is not a valid OS
			[os ...]
		''')

	def test_remove_os_multiple_args(self, host):
		# Add some child data to the os scope, to exercise the plugins
		result = host.run(
			'stack add os attr ubuntu vmware attr=test value=True'
		)
		assert result.rc == 0

		result = host.run(
			'stack add os firewall ubuntu vmware service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run(
			'stack add os route ubuntu vmware address=127.0.0.3 gateway=127.0.0.3'
		)
		assert result.rc == 0

		# Now delete both OSes
		result = host.run('stack remove os ubuntu vmware')
		assert result.rc == 0

		# Make sure ubuntu gone now
		result = host.run('stack list os ubuntu')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "ubuntu" argument is not a valid OS
			[os ...]
		''')

		# The vmware OS should be gone too
		result = host.run('stack list os vmware')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "vmware" argument is not a valid OS
			[os ...]
		''')
