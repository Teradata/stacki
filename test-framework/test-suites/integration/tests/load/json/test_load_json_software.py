import pytest


class TestLoadJsonSoftware:

	"""
	Test that the load json software is able to load what export software exports
	"""

	def test_load_json_software(self, host):
		# export the software data
		results = host.run('stack export software')
		assert results.rc == 0
		initial_software_data = results.stdout

		#write the output to a file
		with open ('software.json', 'w+') as file:
			file.write(initial_software_data)

		#reload the software json file
		results = host.run('stack load json software file=software.json')
		assert results.rc == 0

		# re-export the data and check that nothing has changed
		results = host.run('stack export software')
		assert results.rc == 0
		final_software_data = results.stdout

		assert initial_software_data == final_software_data