import json


class TestRemoveAttr:
	def test_add_and_remove(self, host):
		# Add a test attr
		result = host.run(f'stack set attr attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run(f'stack list attr attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'scope': 'global',
			'type': 'var',
			'value': 'True'
		}]

		# Now remove it
		result = host.run(f'stack remove attr attr=test')
		assert result.rc == 0

		# Make sure it got removed
		result = host.run(f'stack list attr attr=test')
		assert result.rc == 0
		assert result.stdout == ''
