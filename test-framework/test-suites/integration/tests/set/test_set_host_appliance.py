import json
from textwrap import dedent


class TestSetHostAppliance:
	def test_no_hosts(self, host):
		result = host.run('stack set host appliance')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {appliance=string}
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack set host appliance a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {appliance=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set host appliance frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" parameter is required
			{host ...} {appliance=string}
		''')

	def test_invalid_appliance(self, host):
		result = host.run('stack set host appliance frontend-0-0 appliance=test')
		assert result.rc == 255
		assert result.stderr == 'error - appliance parameter not valid\n'

	def test_single_host(self, host, add_appliance, add_host):
		# Set the host appliance
		result = host.run('stack set host appliance backend-0-0 appliance=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout)[0]['appliance'] == 'test'

	def test_multiple_hosts(self, host, add_appliance, add_host):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the host appliance on both backends
		result = host.run(
			'stack set host appliance backend-0-0 backend-0-1 appliance=test'
		)
		assert result.rc == 0

		# Check that the change made it into the database
		for backend in ('backend-0-0', 'backend-0-1'):
			result = host.run(f'stack list host {backend} output-format=json')
			assert result.rc == 0
			assert json.loads(result.stdout)[0]['appliance'] == 'test'
