import json
from textwrap import dedent


class TestLoadStorageController:
	def test_no_args(self, host):
		result = host.run('stack load storage controller')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "file" parameter is required
			{file=string} [processor=string]
		''')

	def test_missing_file(self, host):
		result = host.run('stack load storage controller file=/tmp/foo')
		assert result.rc == 255
		assert result.stderr == 'error - file "/tmp/foo" does not exist\n'

	def test_missing_headers(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_missing_headers.csv'
		)
		assert result.rc == 255
		assert result.stderr == (
			'error - the following required fields are not present in the input file: '
			'array id, name, raid level, slot\n'
		)

	def test_invalid_slot(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_invalid_slot.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - slot "test" must be an integer\n'

	def test_negative_slot(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_negative_slot.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - slot "-1" must be >= 0\n'

	def test_invalid_array_id(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_invalid_array_id.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - array id "test" must be an integer\n'

	def test_negative_array_id(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_negative_array_id.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - array id "-1" must be >= 0\n'

	def test_missing_name(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_missing_name.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - empty host name found in "name" column\n'

	def test_invalid_name(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_invalid_name.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - Cannot find host "a:backend"\n'

	def test_missing_slot(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_missing_slot.csv'
		)
		assert result.rc == 255
		assert result.stderr == 'error - empty value found for "slot" column at line 2\n'

	def test_missing_raid(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_missing_raid.csv'
		)
		assert result.rc == 255
		assert result.stderr == (
			'error - empty value found for "raid level" column at line 2\n'
		)

	def test_missing_array_id(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_missing_array_id.csv'
		)
		assert result.rc == 255
		assert result.stderr == (
			'error - empty value found for "array id" column at line 2\n'
		)

	def test_slot_raid_invalid(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_slot_raid_invalid.csv'
		)
		assert result.rc == 255
		assert result.stderr == (
			'error - raid level must be "0" when slot is "*". See line 2\n'
		)

	def test_duplicate_slot(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_duplicate_slot.csv'
		)
		assert result.rc == 255
		assert result.stderr == (
			'error - duplicate slot "1" found in the spreadsheet at line 3\n'
		)

	def test_mismatch_raid(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_mismatch_raid.csv'
		)
		assert result.rc == 255
		assert result.stderr == (
			'error - RAID level mismatch "1" found in the spreadsheet at line 3\n'
		)

	def test_global_scope(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_global_scope.csv'
		)
		assert result.rc == 0

		result = host.run('stack list storage controller output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'adapter': 6,
				'arrayid': 7,
				'enclosure': 5,
				'options': 'test_options',
				'raidlevel': '1',
				'slot': 2
			},
			{
				'adapter': 6,
				'arrayid': 7,
				'enclosure': 5,
				'options': 'test_options',
				'raidlevel': '1',
				'slot': 3
			},
			{
				'adapter': 6,
				'arrayid': 7,
				'enclosure': 5,
				'options': 'test_options',
				'raidlevel': 'hotspare',
				'slot': 4
			}
		]

	def test_appliance_scope(self, host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_appliance_scope.csv'
		)
		assert result.rc == 0

		result = host.run(
			'stack list appliance storage controller backend output-format=json'
		)
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': 2,
			'appliance': 'backend',
			'arrayid': 4,
			'enclosure': 1,
			'options': 'test_options',
			'raidlevel': '0',
			'slot': 3
		}]

	def test_host_scope(self, host, add_host):
		result = host.run(
			'stack load storage controller '
			'file=/export/test-files/load/storage_controller_host_scope.csv'
		)
		assert result.rc == 0

		result = host.run(
			'stack list host storage controller backend-0-0 output-format=json'
		)
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'adapter': 2,
			'arrayid': 4,
			'enclosure': 1,
			'host': 'backend-0-0',
			'options': 'test_options',
			'raidlevel': '0',
			'slot': 3,
			'source': 'H'
		}]
