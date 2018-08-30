import pytest

class TestLoadJsonGlobal:

	"""
	Test that the load json global is able to load what dump global dumps
	"""

	def test_load_json_global(self, host):
		# dump the global data
		results = host.run('stack dump global')
		assert results.rc == 0
		initial_global_data = results.stdout

		#write the output to a file
		with open ('global.json', 'w+') as file:
			file.write(initial_global_data)

		#reload the global json file
		results = host.run('stack load json global file=global.json')
		assert results.rc == 0

		# re-dump the data and check that nothing has changed
		results = host.run('stack dump global')
		assert results.rc == 0
		final_global_data = results.stdout

		# make sure that they are the same
		value = set(initial_global_data) - set(final_global_data)
		assert not value
