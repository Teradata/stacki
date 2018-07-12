import pytest
import os
from os import listdir
from os.path import isfile, join
import json
import re

@pytest.mark.usefixtures("revert_filesystem")
class TestExportSoftware:

	"""
	Test that exporting the software data works properly
	"""

	def test_export_software_pallet(self, host):

		# test that export software provides accurate pallet information
		dirn = '/export/test-files/export/'
		file = dirn + 'roll-minimal.xml'

		#do an initial rm of the files that are about to be created just in case the test has been run recently
		results = host.run('rm -rf disk1')
		results = host.run('rm -f minimal*.iso')

		# create a minimal pallet using the xml in test-files
		results = host.run(f'stack create pallet {file}')
		assert results.rc == 0

		# determine the name of the new pallet iso
		cwd = os.getcwd()
		files = os.listdir(cwd)
		pattern = re.compile('minimal-.+\.iso')
		try:
			pallet_iso_name = list(filter(pattern.match,files))[0]
		except IndexError:
			raise FileNotFoundError('pallet iso')

		# add the pallet that we have just created
		results = host.run(f'stack add pallet {pallet_iso_name}')
		assert results.rc == 0

		# export our software information
		results = host.run('stack export software')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that our export contains accurate pallet information
		iso_url = '/'.join([cwd, pallet_iso_name])
		check = False
		for pallet in exported_data['software']['pallet']:
			if pallet['name'] == 'minimal' and pallet['url'] == iso_url:
				check = True
		assert check == True

	def test_export_software_box(self, host):

		# test that export software provides accurate box information
		# add a test box to the database
		results = host.run('stack add box test')
		assert results.rc == 0

		# export our software information
		results = host.run('stack export software')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that our export contains accurate box information
		check = False
		for box in exported_data['software']['box']:
			if box['name'] == 'test':
				check = True
		assert check == True

	def test_export_software_cart(self, host):

		# test that export software provides accurate cart information
		# add a test cart to the database
		results = host.run('stack add cart test')
		assert results.rc == 0

		# export our software information
		results = host.run('stack export software')
		assert results.rc == 0
		exported_data = json.loads(results.stdout)

		# check to make sure that our export contains accurate cart information
		check = False
		for cart in exported_data['software']['cart']:
			if cart['name'] == 'test':
				check = True
		assert check == True
