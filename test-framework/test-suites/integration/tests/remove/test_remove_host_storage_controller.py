import json
from textwrap import dedent


class TestRemoveHostStorageController:
	def test_no_args(self, host):
		result = host.run('stack remove host storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_remove(self, host, add_host):
		# Add our controller config
		result = host.run(
			'stack add host storage controller backend-0-0 raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list host storage controller backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': 2,
			'arrayid': 4,
			'enclosure': 1,
			'host': 'backend-0-0',
			'options': '',
			'raidlevel': '0',
			'slot': 3,
			'source': 'H'
		}]

		# Now remove it
		result = host.run('stack remove host storage controller backend-0-0 enclosure=1 adapter=2 slot=3')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list host storage controller backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': None,
			'arrayid': '*',
			'enclosure': None,
			'host': 'backend-0-0',
			'options': '',
			'raidlevel': '0',
			'slot': '*',
			'source': 'G'
		}]
