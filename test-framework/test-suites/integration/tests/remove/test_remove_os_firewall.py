import json
from textwrap import dedent


class TestRemoveOSFirewall:
	def test_no_args(self, host):
		result = host.run('stack remove os firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {rulename=string}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove os firewall test rulename=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid OS
			{os ...} {rulename=string}
		''')

	def test_no_rulename(self, host):
		result = host.run('stack remove os firewall sles')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "rulename" parameter is required
			{os ...} {rulename=string}
		''')

	def test_invalid_rulename(self, host):
		result = host.run('stack remove os firewall sles rulename=test')
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule test does not exist for OS sles\n'

	def test_one_arg(self, host):
		# Add a firewall rule
		result = host.run(
			'stack add os firewall sles service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list os firewall sles output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'os': 'sles',
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
			'source': 'O',
			'type': 'var'
		}]

		# Delete the rule
		result = host.run('stack remove os firewall sles rulename=test')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list os firewall sles')
		assert result.rc == 0
		assert result.stdout == ''

	def test_multiple_args(self, host):
		# Add a firewall rule for our first OS
		result = host.run(
			'stack add os firewall sles service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Add a rule to a second OS too
		result = host.run(
			'stack add os firewall redhat service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure both OSes have their rules in the DB now
		result = host.run('stack list os firewall sles redhat output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'os': 'redhat',
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
				'source': 'O',
				'type': 'var'
			},
			{
				'os': 'sles',
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
				'source': 'O',
				'type': 'var'
			}
		]

		# Delete the OS rules
		result = host.run('stack remove os firewall sles redhat rulename=test')
		assert result.rc == 0

		# Make sure the rules are gone now
		result = host.run('stack list os firewall sles redhat')
		assert result.rc == 0
		assert result.stdout == ''
