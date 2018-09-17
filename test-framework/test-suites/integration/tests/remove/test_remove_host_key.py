import json
from textwrap import dedent


class TestRemoveHostKey:
	def test_remove_host_key_invalid_host(self, host):
		result = host.run('stack remove host key test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_remove_host_key_no_args(self, host):
		result = host.run('stack remove host key')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [id=string]
		''')

	def test_remove_host_key_no_host_matches(self, host):
		result = host.run('stack remove host key a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} [id=string]
		''')

	def test_remove_host_key_no_id(self, host):
		result = host.run('stack remove host key frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "id" parameter is required
			{host} [id=string]
		''')

	def test_remove_host_key_multiple_args(self, host, add_host):
		result = host.run('stack remove host key frontend-0-0 backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} [id=string]
		''')

	def test_remove_host_key_invalid_id(self, host, add_host):
		# Add a key to the backend
		result = host.run('stack add host key backend-0-0 key=foo')
		assert result.rc == 0

		# Get the key's id
		result = host.run('stack list host key backend-0-0 output-format=json')
		assert result.rc == 0
		key_id = json.loads(result.stdout)[0]['id']

		# Now to to remove the key on the wrong host
		result = host.run(f'stack remove host key frontend-0-0 id={key_id}')
		assert result.rc == 255
		assert result.stderr == f"error - public key with id {key_id} doesn't exist for host frontend-0-0\n"

	def test_remove_host_key(self, host):
		# Add a key
		result = host.run('stack add host key frontend-0-0 key=foo')
		assert result.rc == 0

		# Get the key's id
		result = host.run('stack list host key frontend-0-0 output-format=json')
		assert result.rc == 0
		key_id = json.loads(result.stdout)[0]['id']

		# Now to to remove the key
		result = host.run(f'stack remove host key frontend-0-0 id={key_id}')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list host key frontend-0-0')
		assert result.rc == 0
		assert result.stdout == ''
