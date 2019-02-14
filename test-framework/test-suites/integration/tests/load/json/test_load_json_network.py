class TestLoadJsonNetwork:
	"""
	Test that loading network data works properly
	"""

	def skip_test_load_json_network(self, host, test_file):
		# open the file containing the network data, stripping the trailing new line
		path = test_file('load/json/network.json')
		with open(path) as f:
			imported_network_data = f.read().strip()

		# load the data with stack load json
		results = host.run(f'stack load json network file={path}')
		assert results.rc == 0

		# dump the data
		results = host.run('stack dump network')
		assert results.rc == 0
		dumped_network_data = results.stdout.strip()

		# make sure that they are the same
		assert set(dumped_network_data) == set(imported_network_data)
