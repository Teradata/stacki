import json
from textwrap import dedent


class TestAddEnvironmentStorageController:
	def test_no_args(self, host):
		result = host.run('stack add environment storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_all_params(self, host, add_environment):
		result = host.run(
			'stack add environment storage controller test raidlevel=0 enclosure=1 '
			'adapter=2 arrayid=3 slot=4 hotspare=5 options=test_options'
		)
		assert result.rc == 0

		result = host.run('stack list environment storage controller test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'environment': 'test',
				'options': 'test_options',
				'raidlevel': '0',
				'slot': 4
			},
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'environment': 'test',
				'options': 'test_options',
				'raidlevel': 'hotspare',
				'slot': 5
			}
		]
