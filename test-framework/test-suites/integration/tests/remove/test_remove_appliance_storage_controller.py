import json
from textwrap import dedent


class TestRemoveApplianceStorageController:
	def test_no_args(self, host):
		result = host.run('stack remove appliance storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "appliance" argument is required
			{appliance ...} {slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_remove(self, host):
		# Add our controller config
		result = host.run(
			'stack add appliance storage controller backend raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list appliance storage controller backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': 2,
			'appliance': 'backend',
			'arrayid': 4,
			'enclosure': 1,
			'options': '',
			'raidlevel': '0',
			'slot': 3
		}]

		# Now remove it
		result = host.run('stack remove appliance storage controller backend enclosure=1 adapter=2 slot=3')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list appliance storage controller backend')
		assert result.rc == 0
		assert result.stdout == ''
