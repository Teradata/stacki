import json
from textwrap import dedent


class TestAddHostKey:
	def test_no_hosts(self, host):
		result = host.run('stack add host key')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [key=string]
		''')
	
	def test_no_matching_hosts(self, host):
		result = host.run('stack add host key a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [key=string]
		''')
	
	def test_multiple_hosts(self, host, add_host):
		result = host.run('stack add host key frontend-0-0 backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} [key=string]
		''')
	
	def test_no_key(self, host):
		result = host.run('stack add host key frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "key" parameter is required
			{host} [key=string]
		''')
	
	def test_direct(self, host):
		# Add the key
		result = host.run('stack add host key frontend-0-0 key=test_key')
		assert result.rc == 0
		
		# Check that it made it into the database
		result = host.run('stack list host key frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'test_key'
			}
		]
	
	def test_from_file(self, host):
		# Add the key
		result = host.run('stack add host key frontend-0-0 '
			'key=/export/test-files/add/add_host_key.txt')
		assert result.rc == 0
		
		# Check that it made it into the database
		result = host.run('stack list host key frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'test_key'
			}
		]
	
	def test_duplicate(self, host):
		# Add the key
		result = host.run('stack add host key frontend-0-0 key=test_key')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add host key frontend-0-0 key=test_key')
		assert result.rc == 255
		assert result.stderr == 'error - the public key already exists for host frontend-0-0\n'
