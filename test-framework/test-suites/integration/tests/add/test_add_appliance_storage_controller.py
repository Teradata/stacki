import json
from textwrap import dedent


class TestAddApplianceStorageController:
	def test_no_args(self, host):
		result = host.run('stack add appliance storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} {arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_all_params(self, host):
		result = host.run(
			'stack add appliance storage controller backend raidlevel=0 enclosure=1 '
			'adapter=2 arrayid=3 slot=4 hotspare=5 options=test_options'
		)
		assert result.rc == 0

		result = host.run('stack list appliance storage controller backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': 2,
				'appliance': 'backend',
				'arrayid': 3,
				'enclosure': 1,
				'options': 'test_options',
				'raidlevel': '0',
				'slot': 4
			},
			{
				'adapter': 2,
				'appliance': 'backend',
				'arrayid': 3,
				'enclosure': 1,
				'options': 'test_options',
				'raidlevel': 'hotspare',
				'slot': 5
			}
		]
