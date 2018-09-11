import json
from textwrap import dedent


class TestListAppliance:
	def test_list_appliance_invalid(self, host):
		result = host.run('stack list appliance test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid appliance
			[appliance ...]
		''')

	def test_list_appliance_no_args(self, host):
		result = host.run('stack list appliance output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'public': 'yes'
			},
			{
				'appliance': 'barnacle',
				'public': 'no'
			},
			{
				'appliance': 'builder',
				'public': 'no'
			},
			{
				'appliance': 'frontend',
				'public': 'no'
			},
			{
				'appliance': 'replicant',
				'public': 'yes'
			},
			{
				'appliance': 'switch',
				'public': 'no'
			}
		]

	def test_list_appliance_one_arg(self, host):
		result = host.run('stack list appliance backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'public': 'yes'
			}
		]

	def test_list_appliance_multiple_args(self, host):
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
