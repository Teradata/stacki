import pytest


class TestLoadJsonGlobal:

	"""
	Test that the load json global is able to load what export global exports
	"""

	def test_load_json_global(self, host):
		# export the global data
		results = host.run('stack export global')
		assert results.rc == 0
		initial_global_data = results.stdout

		#write the output to a file
		with open ('global.json', 'w+') as file:
			file.write(initial_global_data)

		#reload the global json file
		results = host.run('stack load json global file=global.json')
		assert results.rc == 0

		# re-export the data and check that nothing has changed
		results = host.run('stack export global')
		assert results.rc == 0
		final_global_data = results.stdout

		assert initial_global_data == final_global_data