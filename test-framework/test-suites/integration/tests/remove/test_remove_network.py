import json
from textwrap import dedent


class TestRemoveNetwork:
	def test_no_args(self, host):
		result = host.run('stack remove network')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" argument is required
			{network ...}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove network test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			{network ...}
		''')

	def test_in_use(self, host, add_host, add_environment):
		# Try to remove the private network, which is in use
		result = host.run('stack remove network private')
		assert result.rc == 255
		assert result.stderr == 'error - network "private" in use\n'

	def test_one_arg(self, host, add_network):
		# Remove our test network
		result = host.run('stack remove network test')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list network test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			[network ...]
		''')

	def test_multiple_args(self, host, add_network):
		# Add a second test network
		add_network('foo', '192.168.1.0')

		# Remove our test networks
		result = host.run('stack remove network test foo')
		assert result.rc == 0

		# Make sure test network is gone
		result = host.run('stack list network test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid network
			[network ...]
		''')

		# Make sure foo environment is gone
		result = host.run('stack list network foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid network
			[network ...]
		''')
