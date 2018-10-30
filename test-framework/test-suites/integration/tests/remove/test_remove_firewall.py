import json
from textwrap import dedent


class TestRemoveFirewall:
	def test_no_rulename(self, host):
		result = host.run('stack remove firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "rulename" parameter is required
			{rulename=string}
		''')

	def test_invalid_rulename(self, host):
		result = host.run('stack remove firewall rulename=test')
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule test does not exist\n'

	def test_one_arg(self, host):
		# Add a firewall rule
		result = host.run(
			'stack add firewall service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rules = [
			rule for rule in json.loads(result.stdout)
			if rule['name'] == 'test'
		]
		assert rules == [{
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

		# Delete the rule
		result = host.run('stack remove firewall rulename=test')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list firewall output-format=json')
		assert result.rc == 0

		rules = [
			rule for rule in json.loads(result.stdout)
			if rule['name'] == 'test'
		]
		assert rules == []
