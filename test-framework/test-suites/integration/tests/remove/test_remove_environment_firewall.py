import json
from textwrap import dedent


class TestRemoveEnvironmentFirewall:
	def test_no_args(self, host):
		result = host.run('stack remove environment firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {rulename=string}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove environment firewall test rulename=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid environment
			{environment ...} {rulename=string}
		''')

	def test_no_rulename(self, host, add_environment):
		result = host.run('stack remove environment firewall test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "rulename" parameter is required
			{environment ...} {rulename=string}
		''')

	def test_invalid_rulename(self, host, add_environment):
		result = host.run('stack remove environment firewall test rulename=test')
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule test does not exist for environment test\n'

	def test_one_arg(self, host, add_environment):
		# Add a firewall rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list environment firewall test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'environment': 'test',
			'name': 'test',
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'private',
			'output-network': '',
			'flags': None,
			'comment': None,
			'source': 'E',
			'type': 'var'
		}]

		# Delete the rule
		result = host.run('stack remove environment firewall test rulename=test')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list environment firewall test')
		assert result.rc == 0
		assert result.stdout == ''

	def test_multiple_args(self, host, add_environment):
		# Add a firewall rule for our first environment
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Add a second test environment
		add_environment('foo')

		# It gets a rule too
		result = host.run(
			'stack add environment firewall foo service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure both environments have their rules in the DB now
		result = host.run('stack list environment firewall test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'environment': 'foo',
				'name': 'test',
				'table': 'filter',
				'service': '1234',
				'protocol': 'TCP',
				'chain': 'INPUT',
				'action': 'ACCEPT',
				'network': 'private',
				'output-network': '',
				'flags': None,
				'comment': None,
				'source': 'E',
				'type': 'var'
			},
			{
				'environment': 'test',
				'name': 'test',
				'table': 'filter',
				'service': '1234',
				'protocol': 'TCP',
				'chain': 'INPUT',
				'action': 'ACCEPT',
				'network': 'private',
				'output-network': '',
				'flags': None,
				'comment': None,
				'source': 'E',
				'type': 'var'
			}
		]

		# Delete the environment rules
		result = host.run('stack remove environment firewall test foo rulename=test')
		assert result.rc == 0

		# Make sure the rules are gone now
		result = host.run('stack list environment firewall test foo')
		assert result.rc == 0
		assert result.stdout == ''
