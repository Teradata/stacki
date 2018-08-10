import pytest

class TestLoadJsonAppliance:

	"""
	Test that loading appliance data works properly
	"""

	def test_load_json_appliance(self, host):
		dirn = '/export/test-files/load/json/'
		file = dirn + 'appliance.json'

		# open the file containing the appliance data, stripping the trailing new line
		with open(file) as f: imported_appliance_data = f.read().strip()

		# load the data with stack load json
		results = host.run(f'stack load json appliance file={file}')
		assert results.rc == 0

		# dump the data
		results = host.run('stack dump appliance')
		assert results.rc == 0
		dumped_appliance_data = results.stdout.strip()

		# make sure that they are the same
		value = set(dumped_appliance_data) - set(imported_appliance_data)
		assert not value
