import json
from textwrap import dedent


class TestAddStorageController:
	def test_no_arrayid(self, host):
		result = host.run('stack add storage controller raidlevel=0 slot=2')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "arrayid" parameter is required
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_no_raidlevel(self, host):
		result = host.run('stack add storage controller arrayid=1 slot=2')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "raidlevel" parameter is required
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_no_slot_or_hotspare(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" or "hotspare" parameter is required
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_invalid_adapter(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 adapter=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "adapter" parameter must be an integer
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_negative_adapter(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 adapter=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "adapter" parameter must be >= 0
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_invalid_enclosure(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 enclosure=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "enclosure" parameter must be an integer
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_negative_enclosure(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 enclosure=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "enclosure" parameter must be >= 0
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_invalid_slot(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" parameter must be an integer
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_negative_slot(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" parameter must be >= 0
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_duplicate_slot(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=1,1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "slot" parameter "1" is listed twice
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_existing_slot(self, host):
		# Add it once
		result = host.run('stack add storage controller adapter=1 enclosure=2 slot=3 arrayid=4 raidlevel=0')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add storage controller adapter=1 enclosure=2 slot=3 arrayid=4 raidlevel=0')
		assert result.rc == 255
		assert result.stderr == 'error - disk specification for "1/2/3" already exists\n'

	def test_invalid_hotspare(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 hotspare=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "hotspare" parameter must be an integer
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_negative_hotspare(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 hotspare=-1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "hotspare" parameter must be >= 0
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_duplicate_hotspare(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2 hotspare=1,1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "hotspare" parameter "1" is listed twice
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_existing_hotspare(self, host):
		# Add it once
		result = host.run('stack add storage controller adapter=1 enclosure=2 hotspare=3 arrayid=4 raidlevel=0')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add storage controller adapter=1 enclosure=2 hotspare=3 arrayid=4 raidlevel=0')
		assert result.rc == 255
		assert result.stderr == 'error - disk specification for "1/2/3" already exists\n'

	def test_hotspare_overlap_slots(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=1 hotspare=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "hotspare" parameter "1" is listed in slots
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_invalid_arrayid(self, host):
		result = host.run('stack add storage controller arrayid=test raidlevel=0 slot=2 enclosure=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "arrayid" parameter must be an integer
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_negative_arrayid(self, host):
		result = host.run('stack add storage controller arrayid=-1 raidlevel=0 slot=2 enclosure=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "arrayid" parameter must be >= 1
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_arrayid_global_no_hotspares(self, host):
		result = host.run('stack add storage controller arrayid=global raidlevel=0 slot=2 enclosure=1')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "arrayid" parameter is "global" with no hotspares
			{arrayid=string} [adapter=integer] [enclosure=integer] [hotspare=integer] [raidlevel=integer] [slot=integer]
		''')

	def test_minimal(self, host):
		result = host.run('stack add storage controller arrayid=1 raidlevel=0 slot=2')
		assert result.rc == 0

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
				'adapter': None,
				'arrayid': 1,
				'enclosure': None,
				'options': '',
				'raidlevel': '0',
				'slot': 2
			}
		]

	def test_all_params(self, host):
		result = host.run(
			'stack add storage controller raidlevel=0 enclosure=1 '
			'adapter=2 arrayid=3 slot=4 hotspare=5 options=test'
		)
		assert result.rc == 0

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
				'arrayid': 3,
				'enclosure': 1,
				'options': 'test',
				'raidlevel': '0',
				'slot': 4
			},
			{
				'adapter': 2,
				'arrayid': 3,
				'enclosure': 1,
				'options': 'test',
				'raidlevel': 'hotspare',
				'slot': 5
			}
		]

	def test_global_hotspares(self, host):
		result = host.run('stack add storage controller arrayid=global hotspare=4,5')
		assert result.rc == 0

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
				'adapter': None,
				'arrayid': 'global',
				'enclosure': None,
				'options': '',
				'raidlevel': 'hotspare',
				'slot': 4
			},
			{
				'adapter': None,
				'arrayid': 'global',
				'enclosure': None,
				'options': '',
				'raidlevel': 'hotspare',
				'slot': 5
			}
		]

	def test_stars(self, host):
		result = host.run('stack add storage controller arrayid=* enclosure=1 slot=* raidlevel=5')
		assert result.rc == 0

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
				'adapter': None,
				'arrayid': '*',
				'enclosure': 1,
				'options': '',
				'raidlevel': '5',
				'slot': '*'
			}
		]
