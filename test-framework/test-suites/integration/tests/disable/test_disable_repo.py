import json

class TestDisableRepo:
	def test_disable_repo(self, host, add_repo, revert_etc):
		''' we should be able to enable and disable repos from a box '''
		result = host.run('stack add box test')
		assert result.rc == 0

		# capture empty but existing text box output
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0
		empty_box_output = json.loads(result.stdout)

		result = host.run('stack enable repo test box=test')
		assert result.rc == 0

		# verify box test has repo test
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0
		output = json.loads(result.stdout)
		assert len(output) == 1
		assert output[0]['repos'] == 'test'

		result = host.run('stack disable repo test box=test')
		assert result.rc == 0

		# now verify the box exists but without the test repo
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == empty_box_output

	def test_disable_enable_repo_no_args(self, host):
		''' neither disable nor enable repo should work with no repo specified '''
		result = host.run('stack disable repo')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

		result = host.run('stack enable repo')
		assert result.rc == 255
		assert result.stderr.startswith('error - ')

	def test_disable_enable_repo_default_box(self, host, add_repo, revert_etc):
		''' the box parameter should default to the default box '''
		# capture existing default box output
		result = host.run('stack list box default output-format=json')
		assert result.rc == 0
		default_box_output = json.loads(result.stdout)

		result = host.run('stack enable repo test')
		assert result.rc == 0
		
		result = host.run('stack list box default output-format=json')
		assert result.rc == 0
		output = json.loads(result.stdout)
		assert len(output) == 1
		assert output[0]['repos'] == 'test'

		result = host.run('stack disable repo test')
		assert result.rc == 0

		result = host.run('stack list box default output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == default_box_output

