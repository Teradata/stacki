import pytest
import json

class TestExportGroup:

	"""
	Test that exporting the group data works properly by adding a group
	then exporting it and checking that it is valid
	"""

	def test_export_host(self, host):

		# first lets add a group so we know what to look for in the export
		results = host.run('stack add group test')
		assert results.rc == 0


		# export our group information
		results = host.run('stack export group')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that the information we just added is in the export data
		assert exported_data['group'][0]['name'] == 'test'
		check = False
		for group in exported_data['group']:
			if group['name'] == 'test':
				check = True
		assert check == True

