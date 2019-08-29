import json


class TestLoadAttrfile:
	def test_missing_file(self, host):
		result = host.run(f'stack load attrfile file=/tmp/foo.csv')
		assert result.rc == 255
		assert result.stderr == 'error - file "/tmp/foo.csv" does not exist\n'

	def test_missing_target_column(self, host, test_file):
		path = test_file('load/attrfile_missing_target_column.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == "error - 'target' must be the first column in headers\n"

	def test_unknown_target(self, host, test_file):
		path = test_file('load/attrfile_unknown_target.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "foo"\n'

	def test_unicode_decode_error(self, host, test_file):
		path = test_file('load/attrfile_unicode_decode_error.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - non-ascii character in file\n'

	def test_invalid_attr_space(self, host, test_file):
		path = test_file('load/attrfile_invalid_attr_space.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - attribute "test 1" cannot have a space character\n'

	def test_invalid_attr_multiple_slash(self, host, test_file):
		path = test_file('load/attrfile_invalid_attr_multiple_slash.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - attribute "test/1/1" cannot have more than one "/"\n'

	def test_invalid_attr_dash(self, host, test_file):
		path = test_file('load/attrfile_invalid_attr_dash.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - attribute "test-1" contains an invalid character.\n"test-1" must be a valid ctoken\n'

	def test_global_appliance_host_scope(self, host, add_host, test_file):
		# Load our attr file
		path = test_file('load/attrfile_global_appliance_host_scope.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 0

		# Now list all the host attrs and see if they match what we expect
		result = host.run(
			"stack list host attr backend-0-0 attr='test.*' output-format=json"
		)
		assert result.rc == 0

		with open(test_file('load/attrfile_global_appliance_host_scope.json')) as output:
			assert json.loads(result.stdout) == json.loads(output.read())

	def test_environment_scope(self, host, add_host, add_environment, add_box, test_file):
		# Load our attr file
		path = test_file('load/attrfile_environment_scope.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 0

		# Now list all the host attrs and see if they match what we expect
		result = host.run(
			"stack list host attr backend-0-0 attr='test.*' output-format=json"
		)
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test.environment',
			'host': 'backend-0-0',
			'scope': 'environment',
			'type': 'var',
			'value': 'test_1'
		}]

		# The backend should also be placed in the test environment and box
		result = host.run("stack list host backend-0-0 output-format=json")
		assert result.rc == 0

		data = json.loads(result.stdout)[0]
		assert data['box'] == 'test'
		assert data['environment'] == 'test'

	def test_default_target(self, host, add_host, test_file):
		# Load our attr file
		path = test_file('load/attrfile_default_target.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 0

		# Now list all the host attrs and see if they match what we expect
		result = host.run(
			"stack list host attr backend-0-0 attr='test.*' output-format=json"
		)
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'attr': 'test.default',
				'host': 'backend-0-0',
				'scope': 'host',
				'type': 'var',
				'value': 'test_1'
			},
			{
				'attr': 'test.host',
				'host': 'backend-0-0',
				'scope': 'host',
				'type': 'var',
				'value': 'test_3'
			}
		]

	def test_create_spreadsheet_dirs(self, host, test_file, rmtree):
		# Remove the existing spreadsheets directory
		rmtree('/export/stack/spreadsheets')

		# Confirm the tree is gone
		assert not host.file('/export/stack/spreadsheets').exists

		# Load a spreadsheet, to cause the directories to get created
		path = test_file('load/attrfile_create_spreadsheet_dirs.csv')
		result = host.run(f'stack load attrfile file={path}')
		assert result.rc == 0

		# Make sure they are there now
		assert host.file('/export/stack/spreadsheets').exists
		assert host.file('/export/stack/spreadsheets/RCS').exists
