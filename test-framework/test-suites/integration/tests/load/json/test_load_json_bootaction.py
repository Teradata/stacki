import pytest

@pytest.mark.usefixtures("revert_database")
class TestLoadJsonBootaction:

	"""
	Test that loading bootaction data works properly
	"""

	def test_load_json_bootaction(self, host):
		dirn = '/export/test-files/load/json/'
		file = dirn + 'bootaction.json'

		# open the file containing the bootaction data, stripping the trailing new line
		with open(file) as f: imported_bootaction_data = f.read().strip()

		# load the data with stack load json
		results = host.run(f'stack load json bootaction file={file}')
		assert results.rc == 0

		# export the data
		results = host.run('stack export bootaction')
		assert results.rc == 0
		exported_bootaction_data = results.stdout.strip()

		# make sure that they are the same
		value = set(exported_bootaction_data) - set(imported_bootaction_data)
		assert not value