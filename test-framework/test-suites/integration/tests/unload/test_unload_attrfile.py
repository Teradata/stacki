class TestUnloadAttrfile:
	def test_missing_file(self, host):
		result = host.run(f'stack unload attrfile file=/tmp/foo.csv')
		assert result.rc == 255
		assert result.stderr == 'error - file "/tmp/foo.csv" does not exist\n'

	def test_unknown_target(self, host, test_file):
		path = test_file('unload/attrfile_unknown_target.csv')
		result = host.run(f'stack unload attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "foo"\n'

	def test_unicode_decode_error(self, host, test_file):
		path = test_file('unload/attrfile_unicode_decode_error.csv')
		result = host.run(f'stack unload attrfile file={path}')
		assert result.rc == 255
		assert result.stderr == 'error - non-ascii character in file\n'

	def test_add_report_unload(self, host, add_host, tmp_path):
		# Add a handful of attrs in different scopes
		result = host.run(
			'stack add attr attr=test.global value=test_1'
		)
		assert result.rc == 0

		result = host.run(
			'stack add appliance attr backend attr=test.appliance value=test_2'
		)
		assert result.rc == 0

		result = host.run(
			'stack add host attr backend-0-0 attr=test.host value=test_3'
		)
		assert result.rc == 0

		# Now report our attrfile
		result = host.run("stack report attrfile filter='test\\.'")
		assert result.rc == 0

		# Write it to a temp file
		attrs_csv = tmp_path / 'attr.csv'
		with open(attrs_csv, 'w+') as f:
			f.write(result.stdout)

		# Unload the attrs using the CSV file
		result = host.run(f'stack unload attrfile file={attrs_csv}')
		assert result.rc == 0

		# Make sure the attrs are gone
		result = host.run(
			"stack list host attr backend-0-0 attr='test.*'"
		)
		assert result.rc == 0
		assert result.stdout == ""
