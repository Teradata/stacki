import json


class TestRemoveHostAttr:
	def test_add_and_remove(self, host, add_host):
		# Add a test attr
		result = host.run('stack add host attr backend-0-0 attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list host attr backend-0-0 attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'host': 'backend-0-0',
			'scope': 'host',
			'type': 'var',
			'value': 'True'
		}]

		# Now remove it
		result = host.run(f'stack remove host attr backend-0-0 attr=test')
		assert result.rc == 0

		# Make sure it got removed
		result = host.run(f'stack list host attr backend-0-0 attr=test')
		assert result.rc == 0
		assert result.stdout == ''
