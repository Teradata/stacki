import json
from textwrap import dedent


class TestRemoveEnvironmentStorageController:
	def test_no_args(self, host):
		result = host.run('stack remove environment storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "environment" argument is required
			{environment ...} {slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_remove(self, host, add_environment):
		# Add our controller config
		result = host.run(
			'stack add environment storage controller test raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list environment storage controller test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': 2,
			'arrayid': 4,
			'enclosure': 1,
			'environment': 'test',
			'options': '',
			'raidlevel': '0',
			'slot': 3
		}]

		# Now remove it
		result = host.run(
			'stack remove environment storage controller test enclosure=1 adapter=2 slot=3'
		)
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list environment storage controller test')
		assert result.rc == 0
		assert result.stdout == ''
