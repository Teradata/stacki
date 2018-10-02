import json
from textwrap import dedent


class TestSetHostMetadata:
	def test_set_host_metadata_no_hosts(self, host):
		result = host.run('stack set host metadata')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {metadata=string}
		''')

	def test_set_host_metadata_no_matching_hosts(self, host):
		result = host.run('stack set host metadata a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {metadata=string}
		''')

	def test_set_host_metadata_no_parameters(self, host):
		result = host.run('stack set host metadata frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "metadata" parameter is required
			{host ...} {metadata=string}
		''')

	def test_set_host_metadata_single_host(self, host, add_host):
		# Set the host metadata
		result = host.run('stack set host metadata backend-0-0 metadata=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host attr backend-0-0 attr=metadata output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'const',
			'attr': 'metadata',
			'value': 'test'
		}]

	def test_set_host_metadata_multiple_hosts(self, host, add_host, host_os):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the host metadata on both backends
		result = host.run('stack set host metadata backend-0-0 backend-0-1 metadata=test')
		assert result.rc == 0

		# Check that the change made it into the database
		result = host.run(f'stack list host attr a:backend attr=metadata output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'backend-0-0',
				'scope': 'host',
				'type': 'const',
				'attr': 'metadata',
				'value': 'test'
			},
			{
				'host': 'backend-0-1',
				'scope': 'host',
				'type': 'const',
				'attr': 'metadata',
				'value': 'test'
			}
		]
