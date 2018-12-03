import json
from textwrap import dedent


class TestRemoveOSStorageController:
	def test_no_args(self, host):
		result = host.run('stack remove os storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_remove(self, host):
		# Add our controller config
		result = host.run(
			'stack add os storage controller sles raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list os storage controller sles output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': 2,
			'arrayid': 4,
			'enclosure': 1,
			'options': '',
			'os': 'sles',
			'raidlevel': '0',
			'slot': 3
		}]

		# Now remove it
		result = host.run('stack remove os storage controller sles enclosure=1 adapter=2 slot=3')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list os storage controller sles')
		assert result.rc == 0
		assert result.stdout == ''
