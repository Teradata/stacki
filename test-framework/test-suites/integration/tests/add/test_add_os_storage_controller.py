import json
from textwrap import dedent


class TestAddOSStorageController:
	def test_no_args(self, host):
		result = host.run('stack add os storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_all_params(self, host):
		result = host.run(
			'stack add os storage controller sles raidlevel=0 enclosure=1 '
			'adapter=2 arrayid=3 slot=4 hotspare=5 options=test_options'
		)
		assert result.rc == 0

		result = host.run('stack list os storage controller sles output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'options': 'test_options',
				'os': 'sles',
				'raidlevel': '0',
				'slot': 4
			},
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'options': 'test_options',
				'os': 'sles',
				'raidlevel': 'hotspare',
				'slot': 5
			}
		]
