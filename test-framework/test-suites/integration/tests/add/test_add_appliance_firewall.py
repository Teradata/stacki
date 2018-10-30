import json
import re
from textwrap import dedent

class TestAddApplianceFirewall:
	def test_no_appliances(self, host):
		result = host.run('stack add appliance firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_invalid_appliance(self, host):
		result = host.run('stack add appliance firewall foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid appliance
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_service(self, host):
		result = host.run(
			'stack add appliance firewall frontend chain=INPUT '
			'action=ACCEPT protocol=TCP network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "service" parameter is required
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_chain(self, host):
		result = host.run(
			'stack add appliance firewall frontend service=1234 '
			'action=ACCEPT protocol=TCP network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "chain" parameter is required
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_action(self, host):
		result = host.run(
			'stack add appliance firewall frontend service=1234 '
			'chain=INPUT protocol=TCP network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_protocol(self, host):
		result = host.run(
			'stack add appliance firewall frontend service=1234 '
			'chain=INPUT action=ACCEPT network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "protocol" parameter is required
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_networks(self, host):
		result = host.run(
			'stack add appliance firewall frontend service=1234 '
			'chain=INPUT action=ACCEPT protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" or "output-network" parameter is required
			{appliance ...} {action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_one_appliance(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall frontend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'frontend',
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
			'source': 'A',
			'type': 'var'
		}]
	
	def test_multiple_appliances(self, host, add_host):
		# Add the rules
		result = host.run(
			'stack add appliance firewall frontend backend service=1234 '
			'chain=INPUT action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure they are in the DB now
		for appliancename in ('frontend', 'backend'):
			result = host.run(f'stack list appliance firewall {appliancename} output-format=json')
			assert result.rc == 0
			assert json.loads(result.stdout) == [{
				'appliance': appliancename,
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
				'source': 'A',
				'type': 'var'
			}]

	def test_network_all(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=all rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall frontend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'frontend',
			'name': 'test',
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'all',
			'output-network': '',
			'flags': None,
			'comment': None,
			'source': 'A',
			'type': 'var'
		}]

	def test_invalid_network(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=test rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - network "test" not in the database. Run "stack list network" to get a list of valid networks.\n'

	def test_output_network_all(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=all rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall frontend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'frontend',
			'name': 'test',
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': '',
			'output-network': 'all',
			'flags': None,
			'comment': None,
			'source': 'A',
			'type': 'var'
		}]
	
	def test_output_network_existing(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall frontend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'frontend',
			'name': 'test',
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': '',
			'output-network': 'private',
			'flags': None,
			'comment': None,
			'source': 'A',
			'type': 'var'
		}]

	def test_invalid_output_network(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=test rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - output-network "test" not in the database. Run "stack list network" to get a list of valid networks.\n'

	def test_all_parameters(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend table=nat service=1234 '
			'chain=INPUT action=ACCEPT protocol=TCP network=private '
			'output-network=private flags=test_flag comment=test_comment '
			'rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall frontend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) ==  [{
			'appliance': 'frontend',
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
			'source': 'A',
			'type': 'var'
		}]

	def test_no_rulename(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall frontend output-format=json')
		assert result.rc == 0
		rules = json.loads(result.stdout)

		# Make sure our rule name was a UUID and then remove it for the match
		assert re.match(
			r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
			rules[0]['name']
		)
		del rules[0]['name']

		assert rules == [{
			'appliance': 'frontend',
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'private',
			'output-network': '',
			'flags': None,
			'comment': None,
			'source': 'A',
			'type': 'var'
		}]

	def test_duplicate(self, host):
		# Add the rule
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private'
		)
		assert result.rc == 0

		# Now add it again and make sure it fails
		result = host.run(
			'stack add appliance firewall frontend service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private'
		)
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule already exists\n'
