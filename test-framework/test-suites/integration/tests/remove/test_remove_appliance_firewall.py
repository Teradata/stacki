import json
from textwrap import dedent


class TestRemoveApplianceFirewall:
	def test_no_args(self, host):
		result = host.run('stack remove appliance firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} {rulename=string}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove appliance firewall test rulename=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			{appliance ...} {rulename=string}
		''')

	def test_no_rulename(self, host, add_appliance):
		result = host.run('stack remove appliance firewall test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "rulename" parameter is required
			{appliance ...} {rulename=string}
		''')

	def test_invalid_rulename(self, host, add_appliance):
		result = host.run('stack remove appliance firewall test rulename=test')
		assert result.rc == 255
		assert result.stderr == 'error - rule named "test" does not exist\n'

	def test_one_arg(self, host, add_appliance):
		# Add a firewall rule
		result = host.run(
			'stack add appliance firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list appliance firewall test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'test',
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
			'source': 'A',
			'type': 'var'
		}]

		# Delete the rule
		result = host.run('stack remove appliance firewall test rulename=test')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list appliance firewall test')
		assert result.rc == 0
		assert result.stdout == ''

	def test_multiple_args(self, host, add_appliance):
		# Add a firewall rule for our first appliance
		result = host.run(
			'stack add appliance firewall test service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Add a second test appliance
		add_appliance('foo')

		# It gets a rule too
		result = host.run(
			'stack add appliance firewall foo service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure both appliances have their rules in the DB now
		result = host.run('stack list appliance firewall test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'foo',
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
				'source': 'A',
				'type': 'var'
			},
			{
				'appliance': 'test',
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
				'source': 'A',
				'type': 'var'
			}
		]

		# Delete the appliance rules
		result = host.run('stack remove appliance firewall test foo rulename=test')
		assert result.rc == 0

		# Make sure the rules are gone now
		result = host.run('stack list appliance firewall test foo')
		assert result.rc == 0
		assert result.stdout == ''
