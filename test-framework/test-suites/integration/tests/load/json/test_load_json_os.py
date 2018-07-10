import pytest


class TestLoadJsonOs:

	"""
	Test that the load json os is able to load what export os exports
	"""

	def test_load_json_os(self, host):
		# export the os data
		results = host.run('stack export os')
		assert results.rc == 0
		initial_os_data = results.stdout.strip()

		#write the output to a file
		with open ('os.json', 'w+') as file:
			file.write(initial_os_data)

		#reload the os json file
		results = host.run('stack load json os file=os.json')
		assert results.rc == 0

		# re-export the data and check that nothing has changed
		results = host.run('stack export os')
		assert results.rc == 0
		final_os_data = results.stdout.strip()

		assert initial_os_data == final_os_data