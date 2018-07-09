import pytest


class TestLoadJsonNetwork:

	"""
	Test that loading network data works properly
	"""

	def test_load_json_network(self, host):
		dirn = '/export/test-files/load/json/'
		file = dirn + 'network.json'

		# open the file containing the network data, stripping the trailing new line
		with open(file) as f: imported_network_data = f.read().strip()

		# load the data with stack load json
		results = host.run(f'stack load json network file={file}')
		assert results.rc == 0

		# export the data
		results = host.run('stack export network')
		assert results.rc == 0
		exported_network_data = results.stdout.strip()

		# make sure that they are the same
		assert exported_network_data == imported_network_data