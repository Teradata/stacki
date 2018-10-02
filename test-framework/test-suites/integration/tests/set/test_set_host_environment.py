import json
from textwrap import dedent


class TestSetHostEnvironment:
	def test_set_host_environment_no_hosts(self, host):
		result = host.run('stack set host environment')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {environment=string}
		''')

	def test_set_host_environment_no_matching_hosts(self, host):
		result = host.run('stack set host environment a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {environment=string}
		''')

	def test_set_host_environment_no_parameters(self, host):
		result = host.run('stack set host environment frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" parameter is required
			{host ...} {environment=string}
		''')

	def test_set_host_environment_invalid(self, host):
		result = host.run('stack set host environment frontend-0-0 environment=test')
		assert result.rc == 255
		assert result.stderr == 'error - environment parameter not valid\n'

	def test_set_host_environment_single_host(self, host, add_host, add_environment, host_os):
		# Set the host environment
		result = host.run('stack set host environment backend-0-0 environment=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': 'test',
			'host': 'backend-0-0',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_set_host_environment_multiple_hosts(self, host, add_host, add_environment, host_os):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the host environment on both backends
		result = host.run('stack set host environment backend-0-0 backend-0-1 environment=test')
		assert result.rc == 0

		# Check that the change made it into the database
		result = host.run(f'stack list host a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': 'test',
				'host': 'backend-0-0',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '0'
			},
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': 'test',
				'host': 'backend-0-1',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '1'
			}
		]
