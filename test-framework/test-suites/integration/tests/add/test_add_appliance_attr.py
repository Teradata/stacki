import json
from textwrap import dedent


class TestAddApplianceAttr:
	def test_no_args(self, host):
		result = host.run('stack add appliance attr attr=test value=True')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} {attr=string} {value=string} [shadow=boolean]
		''')

	def test_existing(self, host):
		# Add a test attr
		result = host.run('stack add appliance attr backend attr=test value=True')
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

		# Add the test attr again, which should fail
		result = host.run('stack add appliance attr backend attr=test value=True')
		assert result.rc == 255
		assert result.stderr == 'error - attr "test" already exists\n'
