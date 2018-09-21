import json
from textwrap import dedent


class TestRemoveHostFirewall:
	def test_remove_host_firewall_no_args(self, host):
		result = host.run('stack remove host firewall')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {rulename=string}
		''')

	def test_remove_host_firewall_invalid(self, host, invalid_host):
		result = host.run(
			f'stack remove host firewall {invalid_host} rulename=test'
		)
		assert result.rc == 255
		assert result.stderr == f'error - cannot resolve host "{invalid_host}"\n'

	def test_remove_host_firewall_no_rulename(self, host, add_host):
		result = host.run('stack remove host firewall backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "rulename" parameter is required
			{host ...} {rulename=string}
		''')

	def test_remove_host_firewall_invalid_rulename(self, host, add_host):
		result = host.run('stack remove host firewall backend-0-0 rulename=test')
		assert result.rc == 255
		assert result.stderr == 'error - firewall rule test does not exist for host backend-0-0\n'

	def test_remove_host_firewall_one_arg(self, host, add_host):
		# Add a firewall rule
		result = host.run(
			'stack add host firewall backend-0-0 service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure it is in the DB now
		result = host.run('stack list host firewall backend-0-0 output-format=json')
		assert result.rc == 0

		rules = [
			rule for rule in json.loads(result.stdout)
			if rule['name'] == 'test'
		]
		assert rules == [{
			'host': 'backend-0-0',
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
			'source': 'H',
			'type': 'var'
		}]

		# Delete the rule
		result = host.run('stack remove host firewall backend-0-0 rulename=test')
		assert result.rc == 0

		# Make sure it is gone now
		result = host.run('stack list host firewall backend-0-0 output-format=json')
		assert result.rc == 0

		rules = [
			rule for rule in json.loads(result.stdout)
			if rule['name'] == 'test'
		]
		assert rules == []

	def test_remove_host_firewall_multiple_args(self, host, add_host):
		# Add a firewall rule for our first host
		result = host.run(
			'stack add host firewall backend-0-0 service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Add a second test host
		add_host('backend-0-1', '0', '1', 'backend')

		# It gets a rule too
		result = host.run(
			'stack add host firewall backend-0-1 service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		# Make sure both hosts have their rules in the DB now
		result = host.run('stack list host firewall backend-0-0 backend-0-1 output-format=json')
		assert result.rc == 0

		rules = [
			rule for rule in json.loads(result.stdout)
			if rule['name'] == 'test'
		]
		assert rules == [
			{
				'host': 'backend-0-0',
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
				'source': 'H',
				'type': 'var'
			},
			{
				'host': 'backend-0-1',
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
				'source': 'H',
				'type': 'var'
			}
		]

		# Delete the host rules
		result = host.run('stack remove host firewall backend-0-0 backend-0-1 rulename=test')
		assert result.rc == 0

		# Make sure the rules are gone now
		result = host.run('stack list host firewall backend-0-0 backend-0-1 output-format=json')
		assert result.rc == 0

		rules = [
			rule for rule in json.loads(result.stdout)
			if rule['name'] == 'test'
		]
		assert rules == []
