import json


class TestListHostKey:
	def test_list_host_key_invalid(self, host):
		result = host.run('stack list host key test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_list_host_key_no_args(self, host, add_host):
		# Add a few keys
		result = host.run('stack add host key frontend-0-0 key=frontend_key')
		assert result.rc == 0

		result = host.run('stack add host key backend-0-0 key=backend_key')
		assert result.rc == 0

		# Make sure a list shows them
		result = host.run('stack list host key output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'frontend_key'
			},
			{
				'host': 'backend-0-0',
				'id': 2,
				'public key': 'backend_key'
			}
		]

	def test_list_host_key_one_arg(self, host, add_host):
		# Add a few keys for the frontend
		result = host.run('stack add host key frontend-0-0 key=frontend_key_1')
		assert result.rc == 0

		result = host.run('stack add host key frontend-0-0 key=frontend_key_2')
		assert result.rc == 0

		# Add one for the backend so we can make sure the list doesn't include it
		result = host.run('stack add host key backend-0-0 key=backend_key')
		assert result.rc == 0

		# Make sure only the frontend aliases are listed
		result = host.run('stack list host key frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'frontend_key_1'
			},
			{
				'host': 'frontend-0-0',
				'id': 2,
				'public key': 'frontend_key_2'
			}
		]

	def test_list_host_key_multiple_args(self, host, add_host):
		# Add a few keys for the frontend
		result = host.run('stack add host key frontend-0-0 key=frontend_key_1')
		assert result.rc == 0

		result = host.run('stack add host key frontend-0-0 key=frontend_key_2')
		assert result.rc == 0

		# Add a few for backend-0-0
		result = host.run('stack add host key backend-0-0 key=backend_key_1')
		assert result.rc == 0

		result = host.run('stack add host key backend-0-0 key=backend_key_2')
		assert result.rc == 0

		# Add another backend so we can make sure it is skipped in the listing
		add_host('backend-0-1', '0', '2', 'backend')

		# Add a few for backend-0-1
		result = host.run('stack add host key backend-0-1 key=backend_key_3')
		assert result.rc == 0

		result = host.run('stack add host key backend-0-1 key=backend_key_4')
		assert result.rc == 0

		# Now, make sure only the frontend and backend-0-0 keys are listed
		result = host.run('stack list host key frontend-0-0 backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'frontend_key_1'
			},
			{
				'host': 'frontend-0-0',
				'id': 2,
				'public key': 'frontend_key_2'
			},
			{
				'host': 'backend-0-0',
				'id': 3,
				'public key': 'backend_key_1'
			},
			{
				'host': 'backend-0-0',
				'id': 4,
				'public key': 'backend_key_2'
			}
		]

	def test_list_host_key_with_multiple_lines(self, host):
		# Add a key for the frontend with a newline
		result = host.run('stack add host key frontend-0-0 key="frontend_key_1\nfrontend_key_2"')
		assert result.rc == 0

		# Now, make sure both keys are output
		result = host.run('stack list host key frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'frontend_key_1'
			},
			{
				'host': 'frontend-0-0',
				'id': 1,
				'public key': 'frontend_key_2'
			}
		]
