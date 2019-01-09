import json
import re
from textwrap import dedent


class TestAddEnvironmentFirewall:
	def test_no_environments(self, host):
		result = host.run('stack add environment firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_invalid_environment(self, host):
		result = host.run('stack add environment firewall foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid environment
			{environment ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_service(self, host, add_environment):
		result = host.run(
			'stack add environment firewall test chain=INPUT action=ACCEPT protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "service" parameter is required
			{environment ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_chain(self, host, add_environment):
		result = host.run(
			'stack add environment firewall test service=1234 action=ACCEPT protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "chain" parameter is required
			{environment ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_action(self, host, add_environment):
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{environment ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_protocol(self, host, add_environment):
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT action=ACCEPT'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "protocol" parameter is required
			{environment ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_one_environment(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP rulename=test'
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
			'network': None,
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'E',
			'type': 'var'
		}]

	def test_multiple_environments(self, host, add_environment):
		add_environment('foo')

		# Add the rules
		result = host.run(
			'stack add environment firewall test foo service=1234 '
			'chain=INPUT action=ACCEPT protocol=TCP rulename=test'
		)
		assert result.rc == 0

		# Make sure they are in the DB now
		for environment in ('test', 'foo'):
			result = host.run(f'stack list environment firewall {environment} output-format=json')
			assert result.rc == 0
			assert json.loads(result.stdout) == [{
				'environment': environment,
				'name': 'test',
				'table': 'filter',
				'service': '1234',
				'protocol': 'TCP',
				'chain': 'INPUT',
				'action': 'ACCEPT',
				'network': None,
				'output-network': None,
				'flags': None,
				'comment': None,
				'source': 'E',
				'type': 'var'
			}]

	def test_network_existing(self, host, add_environment):
		# Add the rule
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
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'E',
			'type': 'var'
		}]

	def test_invalid_network(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=test rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - "test" is not a valid network\n'

	def test_output_network_existing(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=private rulename=test'
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
			'network': None,
			'output-network': 'private',
			'flags': None,
			'comment': None,
			'source': 'E',
			'type': 'var'
		}]

	def test_invalid_output_network(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=test rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - "test" is not a valid network\n'

	def test_all_parameters(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test table=nat service=1234 '
			'chain=INPUT action=ACCEPT protocol=TCP network=private '
			'output-network=private flags=test_flag comment=test_comment '
			'rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list environment firewall test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) ==  [{
			'environment': 'test',
			'name': 'test',
			'table': 'nat',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'private',
			'output-network': 'private',
			'flags': 'test_flag',
			'comment': 'test_comment',
			'source': 'E',
			'type': 'var'
		}]

	def test_no_rulename(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT action=ACCEPT protocol=TCP'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list environment firewall test output-format=json')
		assert result.rc == 0
		rules = json.loads(result.stdout)

		# Make sure our rule name was a UUID and then remove it for the match
		assert re.match(
			r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
			rules[0]['name']
		)
		del rules[0]['name']

		assert rules == [{
			'environment': 'test',
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': None,
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'E',
			'type': 'var'
		}]

	def test_duplicate(self, host, add_environment):
		# Add the rule
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT action=ACCEPT protocol=TCP'
		)
		assert result.rc == 0

		# Now add it again and make sure it fails
		result = host.run(
			'stack add environment firewall test service=1234 chain=INPUT action=ACCEPT protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule already exists\n'
