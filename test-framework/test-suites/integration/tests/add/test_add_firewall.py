import json
import re
from textwrap import dedent

import jmespath


class TestAddFirewall:
	def test_no_parameters(self, host):
		result = host.run('stack add firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "chain" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_service(self, host):
		result = host.run('stack add firewall chain=INPUT action=ACCEPT protocol=TCP')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "service" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_blank_service(self, host):
		result = host.run('stack add firewall service="" chain=INPUT action=ACCEPT protocol=TCP')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "service" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_invalid_service_range(self, host):
		result = host.run('stack add firewall service=1:2:3 chain=INPUT action=ACCEPT protocol=TCP')
		assert result.rc == 255
		assert result.stderr == 'error - "1:2:3" is not a valid service specification\n'

	def test_invalid_service_port(self, host):
		result = host.run('stack add firewall service=0foo chain=INPUT action=ACCEPT protocol=TCP'
		)
		assert result.rc == 255
		assert result.stderr == 'error - "0foo" is not a valid service specification\n'

	def test_no_chain(self, host):
		result = host.run('stack add firewall service=1234 action=ACCEPT protocol=TCP')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "chain" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_blank_chain(self, host):
		result = host.run('stack add firewall service=1234 chain="" action=ACCEPT protocol=TCP')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "chain" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_action(self, host):
		result = host.run('stack add firewall service=1234 chain=INPUT protocol=TCP')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_blank_action(self, host):
		result = host.run('stack add firewall service=1234 chain=INPUT action="" protocol=TCP')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_no_protocol(self, host):
		result = host.run('stack add firewall service=1234 chain=INPUT action=ACCEPT')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "protocol" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_blank_protocol(self, host):
		result = host.run('stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=""')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "protocol" parameter is required
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_invalid_table(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall table=foo service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "table" parameter is not valid
			{action=string} {chain=string} {protocol=string} {service=string} [comment=string] [flags=string] [network=string] [output-network=string] [rulename=string] [table=string]
		''')

	def test_minimal(self, host):
		# Add the rule
		result = host.run('stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=test')
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
			'network': None,
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]

	def test_network_existing(self, host):
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
			'output-network': None,
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
		assert result.stderr == 'error - "test" is not a valid network\n'

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
			'network': None,
			'output-network': 'private',
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
			'network': None,
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
		assert result.stderr == 'error - "test" is not a valid network\n'

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
			'output-network': None,
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
			'chain=INPUT action=ACCEPT protocol="all" network="" '
			'output-network="" flags="" comment="" '
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
			'protocol': 'all',
			'chain': 'INPUT',
			'action': 'ACCEPT',
			'network': None,
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]

	def test_no_rulename(self, host):
		# Add the rule
		result = host.run('stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP')
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
			'network': None,
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]

	def test_empty_rulename(self, host):
		# Add the rule
		result = host.run('stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=""')
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
			'network': None,
			'output-network': None,
			'flags': None,
			'comment': None,
			'source': 'G',
			'type': 'var'
		}]

	def test_duplicate_name(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=test'
		)
		assert result.rc == 0

		# Now add it again and make sure it fails
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == 'error - rule named "test" already exists\n'

	def test_duplicate_params(self, host):
		# Add the rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=foo'
		)
		assert result.rc == 0

		# Now add it again and make sure it fails
		result = host.run(
			'stack add firewall service=1234 chain=INPUT action=ACCEPT protocol=TCP rulename=bar'
		)
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule already exists\n'
