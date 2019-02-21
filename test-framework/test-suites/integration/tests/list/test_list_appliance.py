import json
from textwrap import dedent


class TestListAppliance:
	def test_invalid(self, host):
		result = host.run('stack list appliance test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			[appliance ...]
		''')

	def test_no_args(self, host):
		result = host.run('stack list appliance output-format=json')
		assert result.rc == 0

		# Make sure some common appliances exist
		output = json.loads(result.stdout)
		assert {
			'appliance': 'backend',
			'public': 'yes'
		} in output

		assert {
			'appliance': 'barnacle',
			'public': 'no'
		} in output

		assert {
			'appliance': 'frontend',
			'public': 'no'
		} in output

		assert {
			'appliance': 'switch',
			'public': 'no'
		} in output

	def test_one_arg(self, host):
		result = host.run('stack list appliance backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'public': 'yes'
			}
		]

	def test_multiple_args(self, host):
		result = host.run('stack list appliance frontend backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'frontend',
				'public': 'no'
			},
			{
				'appliance': 'backend',
				'public': 'yes'
			}
		]
