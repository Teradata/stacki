import pytest


class TestLoadJsonGroup:

	"""
	Test that the load json group is able to load what export group exports
	"""

	def test_load_json_group(self, host):
		# export the group data
		results = host.run('stack export group')
		assert results.rc == 0
		initial_group_data = results.stdout

		#write the output to a file
		with open ('group.json', 'w+') as file:
			file.write(initial_group_data)

		#reload the group json file
		results = host.run('stack load json group file=group.json')
		assert results.rc == 0

		# re-export the data and check that nothing has changed
		results = host.run('stack export group')
		assert results.rc == 0
		final_group_data = results.stdout

		assert initial_group_data == final_group_data