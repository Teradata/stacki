class TestLoadJsonBootaction:
	"""
	Test that loading bootaction data works properly
	"""

	def skip_test_load_json_bootaction(self, host, test_file):
		# open the file containing the bootaction data, stripping the trailing new line
		path = test_file('load/json/bootaction.json')
		with open(path) as f:
			imported_bootaction_data = f.read().strip()

		# load the data with stack load json
		results = host.run(f'stack load json bootaction file={path}')
		assert results.rc == 0

		# dump the data
		results = host.run('stack dump bootaction')
		assert results.rc == 0
		dumped_bootaction_data = results.stdout.strip()

		# make sure that they are the same
		value = set(imported_bootaction_data) - set(dumped_bootaction_data)
		assert not value
