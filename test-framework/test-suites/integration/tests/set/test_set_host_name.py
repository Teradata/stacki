import json
from textwrap import dedent


class TestSetHostName:
	def test_no_hosts(self, host):
		result = host.run('stack set host name')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {name=string}
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack set host name a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {name=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set host name frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "name" parameter is required
			{host} {name=string}
		''')

	def test_already_used(self, host, add_host):
		result = host.run('stack set host name backend-0-0 name=frontend-0-0')
		assert result.rc == 255
		assert result.stderr == 'error - name already exists\n'

	def test_invalid_name(self, host, add_host):
		result = host.run('stack set host name backend-0-0 name=-bad-backend')
		assert result.rc == 255
		errmsg = result.stderr.split('\n')[0]
		assert errmsg == 'error - "name" parameter must be a valid hostname label'

	def test_single_host(self, host, add_host, host_os):
		# Set the host name
		result = host.run('stack set host name backend-0-0 name=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': None,
			'host': 'test',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_multiple_hosts(self, host, add_host):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Try to set the host name on both backends. It should fail.
		result = host.run('stack set host name backend-0-0 backend-0-1 name=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} {name=string}
		''')
