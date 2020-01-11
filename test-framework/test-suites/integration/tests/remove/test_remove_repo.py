import json

class TestRemoveRepo:
	def test_no_args(self, host):
		result = host.run('stack remove repo')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_invalid(self, host):
		result = host.run('stack remove repo test')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_args(self, host, add_repo):
		''' ensure removing one repo only touches that repo '''
		add_repo('test2', 'testurl2')

		result = host.run('stack list repo output-format=json')
		assert result.rc == 0
		two_repo_output = json.loads(result.stdout)
		assert len(two_repo_output) == 2

		result = host.run('stack remove repo test2')
		assert result.rc == 0

		result = host.run('stack list repo output-format=json')
		assert result.rc == 0
		output = json.loads(result.stdout)
		assert len(output) == 1
		assert output[0]['name'] == 'test'

		# add it back and remove both, ensuring they're gone
		add_repo('test2', 'testurl2')
		result = host.run('stack list repo output-format=json')
		assert result.rc == 0
		two_repo_output == json.loads(result.stdout)

		result = host.run('stack remove repo test test2')
		assert result.rc == 0

		result = host.run('stack list repo output-format=json')
		assert result.rc == 0
		assert result.stdout == ''
