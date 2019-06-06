import json


class TestRemoveApplianceAttr:
	def test_add_and_remove(self, host):
		# Add a test attr
		result = host.run('stack set appliance attr backend attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run('stack list appliance attr backend attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'attr': 'test',
			'scope': 'appliance',
			'type': 'var',
			'value': 'True'
		}]

		# Now remove it
		result = host.run(f'stack remove appliance attr backend attr=test')
		assert result.rc == 0

		# Make sure it got removed
		result = host.run(f'stack list appliance attr backend attr=test')
		assert result.rc == 0
		assert result.stdout == ''
