import json
from textwrap import dedent


class TestRemoveStorageController:
	def test_invalid_adapter(self, host):
		result = host.run('stack remove storage controller slot=* adapter=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "adapter" parameter must be an integer
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_negative_adapter(self, host):
		result = host.run('stack remove storage controller slot=* adapter=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "adapter" parameter must be >= 0
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_invalid_enclosure(self, host):
		result = host.run('stack remove storage controller slot=* enclosure=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "enclosure" parameter must be an integer
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_negative_enclosure(self, host):
		result = host.run('stack remove storage controller slot=* enclosure=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "enclosure" parameter must be >= 0
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_invalid_slot(self, host):
		result = host.run('stack remove storage controller slot=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" parameter must be an integer
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_negative_slot(self, host):
		result = host.run('stack remove storage controller slot=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" parameter must be >= 0
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_no_matches_on_adapter(self, host):
		result = host.run('stack remove storage controller adapter=1 enclosure=* slot=*')
		assert result.rc == 255
		assert result.stderr == 'error - disk specification for "1/*/*" doesn\'t exist\n'

	def test_no_matches_on_enclosure(self, host):
		result = host.run('stack remove storage controller adapter=* enclosure=1 slot=*')
		assert result.rc == 255
		assert result.stderr == 'error - disk specification for "*/1/*" doesn\'t exist\n'

	def test_duplicate_slot(self, host):
		result = host.run('stack remove storage controller slot=1,1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" parameter "1" is listed twice
			{slot=integer} [adapter=integer] [enclosure=integer]
		''')

	def test_remove_single_slot(self, host):
		# Add a global rule
		result = host.run(
			'stack add storage controller raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list storage controller output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': None,
				'arrayid': '*',
				'enclosure': None,
				'options': '',
				'raidlevel': '0',
				'slot': '*'
			},
			{
				'adapter': 2,
				'arrayid': 4,
				'enclosure': 1,
				'options': '',
				'raidlevel': '0',
				'slot': 3
			}
		]

		# Now remove it
		result = host.run('stack remove storage controller enclosure=1 adapter=2 slot=3')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list storage controller output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': None,
			'arrayid': '*',
			'enclosure': None,
			'options': '',
			'raidlevel': '0',
			'slot': '*'
		}]

	def test_remove_everything(self, host):
		# Add a global rule
		result = host.run(
			'stack add storage controller raidlevel=0 enclosure=1 '
			'adapter=2 slot=3 arrayid=4'
		)
		assert result.rc == 0

		# Make sure it got added
		result = host.run('stack list storage controller output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': None,
				'arrayid': '*',
				'enclosure': None,
				'options': '',
				'raidlevel': '0',
				'slot': '*'
			},
			{
				'adapter': 2,
				'arrayid': 4,
				'enclosure': 1,
				'options': '',
				'raidlevel': '0',
				'slot': 3
			}
		]

		# Now remove everything
		result = host.run('stack remove storage controller enclosure=* adapter=* slot=*')
		assert result.rc == 0

		# Make sure it's all gone
		result = host.run('stack list storage controller')
		assert result.rc == 0
		assert result.stdout == ''
