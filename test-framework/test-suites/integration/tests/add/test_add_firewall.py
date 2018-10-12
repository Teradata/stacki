import json
import re
from textwrap import dedent

import jmespath

class TestAddFirewall:
	def test_no_parameters(self, host):
		result = host.run('stack add firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "service" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_service(self, host):
		result = host.run(
			'stack add firewall chain=INPUT action=ACCEPT protocol=TCP '
			'network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "service" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_invalid_service_range(self, host):
		result = host.run(
			'stack add firewall service=1:2:3 chain=INPUT action=ACCEPT '
			'protocol=TCP network=private'
		)
		assert result.rc == 255
		assert result.stderr == 'error - port range "1:2:3" is invalid. it must be "integer:integer"\n'
	
	def test_invalid_service_port(self, host):
		result = host.run(
			'stack add firewall service=0foo chain=INPUT action=ACCEPT '
			'protocol=TCP network=private'
		)
		assert result.rc == 255
		assert result.stderr == 'error - port specification "0foo" is invalid. it must be "integer" or "integer:integer"\n'
	
	def test_no_chain(self, host):
		result = host.run(
			'stack add firewall service=1234 action=ACCEPT protocol=TCP '
			'network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "chain" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_action(self, host):
		result = host.run(
			'stack add firewall service=1234 chain=INPUT protocol=TCP '
			'network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_protocol(self, host):
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT '
			'network=private'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "protocol" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_no_networks(self, host):
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT '
			'protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "network" or "output-network" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_invalid_table(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall table=foo service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "table" parameter is not valid
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')
	
	def test_single_arg(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]
	
	def test_network_all(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=all rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]

	def test_invalid_network(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=test rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - network "test" not in the database. Run "stack list network" to get a list of valid networks.\n'

	def test_network_empty_string(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT '
			'protocol=TCP network="" output-network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]
	
	def test_output_network_all(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=all rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]
	
	def test_output_network_existing(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]

	def test_invalid_output_network(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP output-network=test rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - output-network "test" not in the database. Run "stack list network" to get a list of valid networks.\n'

	def test_output_network_empty_string(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT '
			'protocol=TCP network=private output-network="" rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]
		
	def test_all_parameters(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall table=nat service=1234 '
			'chain=INPUT action=ACCEPT protocol=TCP network=private '
			'output-network=private flags=test_flag comment=test_comment '
			'rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
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
			'source': 'G',
			'type': 'var'
		}]

	def test_empty_parameters(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall table=nat service=1234 '
			'chain=INPUT action=ACCEPT protocol="" network=private '
			'output-network=private flags="" comment="" '
			'rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?name=='test']", json.loads(result.stdout))
		assert rule == [{
			'name': 'test',
			'table': 'nat',
			'service': '1234',
			'protocol': None,
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'private',
			'output-network': 'private',
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]
	
	def test_no_rulename(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?service=='1234']", json.loads(result.stdout))
		
		# Make sure our rule name was a UUID and then remove it for the match
		assert re.match(
			r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
			rule[0]['name']
		)
		del rule[0]['name']

		assert rule == [{
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'private',
			'output-network': '',
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]

	def test_empty_rulename(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=""'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rule = jmespath.search("[?service=='1234']", json.loads(result.stdout))
		
		# Make sure our rule name was a UUID and then remove it for the match
		assert re.match(
			r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
			rule[0]['name']
		)
		del rule[0]['name']

		assert rule == [{
			'table': 'filter',
			'service': '1234',
			'protocol': 'TCP',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': 'private',
			'output-network': '',
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]
	
	def test_duplicate(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Now add it again and make sure it fails
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - Rule with rulename "test" already exists\n'
