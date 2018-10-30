import json
from textwrap import dedent


class TestRemoveAppliance:
	def test_no_args(self, host):
		result = host.run('stack remove appliance')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{name}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove appliance test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			{name}
		''')

	def test_backend(self, host):
		# Try to remove the "backend" appliance, which isn't allowed
		result = host.run('stack remove appliance backend')
		assert result.rc == 255
		assert result.stderr == 'error - cannot remove default appliance\n'

	def test_in_use(self, host):
		# Try to remove the "frontend" appliance, which is in use
		result = host.run('stack remove appliance frontend')
		assert result.rc == 255
		assert result.stderr == 'error - cannot remove appliance "frontend" because host "frontend-0-0" is assigned to it\n'

	def test_one_arg(self, host, add_appliance):
		# Add some appliance scoped data to exercise the plugins
		result = host.run('stack add appliance attr test attr=test value=true')
		assert result.rc == 0

		result = host.run(
			'stack add appliance firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run('stack add appliance route test address=192.168.0.2 gateway=private')
		assert result.rc == 0

		# Remove our test appliance
		result = host.run('stack remove appliance test')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list appliance test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			[appliance ...]
		''')

	def test_multiple_args(self, host, add_appliance):
		# Add a second test appliance
		add_appliance('foo')

		# Add some appliance scoped data to exercise the plugins
		result = host.run('stack add appliance attr foo attr=test value=true')
		assert result.rc == 0

		result = host.run(
			'stack add appliance firewall foo service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run('stack add appliance route foo address=192.168.0.2 gateway=private')
		assert result.rc == 0

		# Remove our test appliances
		result = host.run('stack remove appliance test foo')
		assert result.rc == 0

		# Make sure test appliance is gone
		result = host.run('stack list appliance test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			[appliance ...]
		''')

		# Make sure foo appliance is gone
		result = host.run('stack list appliance foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid appliance
			[appliance ...]
		''')
