import json


class TestRemoveEnvironmentAttr:
	def test_add_and_remove(self, host, add_environment):
		# Add a test attr
		result = host.run('stack set environment attr test attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list environment attr test attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'environment': 'test',
			'scope': 'environment',
			'type': 'var',
			'value': 'True'
		}]

		# Add the test attr again with a different value
		result = host.run(f'stack remove environment attr test attr=test')
		assert result.rc == 0

		# Make sure it got removed
		result = host.run(f'stack list environment attr test attr=test')
		assert result.rc == 0
		assert result.stdout == ''
