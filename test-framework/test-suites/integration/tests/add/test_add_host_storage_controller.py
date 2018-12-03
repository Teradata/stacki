import json
from textwrap import dedent


class TestAddHostStorageController:
	def test_no_args(self, host):
		result = host.run('stack add host storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_all_params(self, host, add_host):
		result = host.run(
			'stack add host storage controller backend-0-0 raidlevel=0 enclosure=1 '
			'adapter=2 arrayid=3 slot=4 hotspare=5 options=test_options'
		)
		assert result.rc == 0

		result = host.run('stack list host storage controller backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'host': 'backend-0-0',
				'options': 'test_options',
				'raidlevel': '0',
				'slot': 4,
				'source': 'H'
			},
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'host': 'backend-0-0',
				'options': 'test_options',
				'raidlevel': 'hotspare',
				'slot': 5,
				'source': 'H'
			}
		]
