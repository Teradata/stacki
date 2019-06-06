import json


class TestAddAttr:
	def test_existing(self, host):
		# Add a test attr
		result = host.run('stack add attr attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list attr attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'scope': 'global',
			'type': 'var',
			'value': 'True'
		}]

		# Add the test attr again, which should fail
		result = host.run('stack add attr attr=test value=False')
		assert result.rc == 255
		assert result.stderr == 'error - attr "test" already exists\n'
