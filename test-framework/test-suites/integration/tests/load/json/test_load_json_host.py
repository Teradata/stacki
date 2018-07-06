import pytest


class TestLoadJsonHost:

	"""
	Test that the load json host is able to load what export host exports
	"""

	def test_load_json_host(self, host):
		# export the host data
		results = host.run('stack export host')
		assert results.rc == 0
		initial_host_data = results.stdout

		#write the output to a file
		with open ('host.json', 'w+') as file:
			file.write(initial_host_data)

		#reload the host json file
		results = host.run('stack load json host file=host.json')
		assert results.rc == 0

		# re-export the data and check that nothing has changed
		results = host.run('stack export host')
		assert results.rc == 0
		final_host_data = results.stdout

		assert initial_host_data == final_host_data