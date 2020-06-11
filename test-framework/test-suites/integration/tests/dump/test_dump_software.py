import pytest

import os
from pathlib import Path
from os import listdir
from os.path import isfile, join
import json
import re
import shlex

ADD_REPO_ARGUMENTS = [
	['"test repo"', ('url=http://www.test.url.example.com/',), 'dump/repo-name-with-spaces.json'],
	['test1', ('url=test1.url', 'autorefresh=yes', 'assumeyes=yes', 'gpgcheck=true', 'gpgkey=somekey.asc'), 'dump/repo-with-multiple-params.json'],
	['test_with_templating', ("'url=http://{ Kickstart_PrivateAddress }}/install/pallets/fake/'",), 'dump/templated_url_repo.json'],
]


class TestDumpSoftware:
	"""
	Test that dumping the software data works properly
	"""

	def test_pallet(self, host, revert_export_stack_pallets, test_file, revert_pallet_hooks):
		"test that dump software provides accurate pallet information"

		# do an initial rm of the files that are about to be created just in case the test has been run recently
		results = host.run('rm -rf disk1')
		results = host.run('rm -f minimal*.iso')

		# create a minimal pallet using the xml
		results = host.run(f'stack create pallet {test_file("dump/roll-minimal.xml")}')
		assert results.rc == 0

		# determine the name of the new pallet iso
		cwd = os.getcwd()
		files = os.listdir(cwd)
		pattern = re.compile(r'minimal-.+\.iso')
		try:
			pallet_iso_name = list(filter(pattern.match,files))[0]
		except IndexError:
			raise FileNotFoundError('pallet iso')

		# add the pallet that we have just created
		results = host.run(f'stack add pallet {pallet_iso_name}')
		assert results.rc == 0

		# dump our software information
		results = host.run('stack dump pallet')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that our dump contains accurate pallet information
		iso_url = '/'.join([cwd, pallet_iso_name])
		check = False
		for pallet in dumped_data['software']['pallet']:
			if pallet['name'] == 'minimal' and pallet['url'] == iso_url:
				check = True
		assert check == True

	def test_box(self, host):

		# test that dump software provides accurate box information
		# add a test box to the database
		results = host.run('stack add box test')
		assert results.rc == 0

		# dump our software information
		results = host.run('stack dump box')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that our dump contains accurate box information
		check = False
		for box in dumped_data['software']['box']:
			if box['name'] == 'test':
				check = True
		assert check == True

	def test_repo(self, host, add_repo):
		results = host.run('stack dump repo')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that our dump contains accurate cart information
		check = False
		for repo in dumped_data['software']['repo']:
			if repo['name'] == 'test':
				check = True
		assert check == True

	@pytest.mark.parametrize("repo_args", ADD_REPO_ARGUMENTS)
	def test_load_dumped_repo(self, host, repo_args, stack_load, test_file, fake_os_sles, revert_etc):
		expected_dumpfile = Path(test_file(repo_args[2])).resolve()

		repo_name = repo_args[0]
		repo_args = ' '.join(repo_args[1])

		# setup the test data
		results = host.run(f'stack add repo {repo_name} {repo_args}')
		assert results.rc == 0

		# keep the stack list output for later comparison
		results = host.run(f'stack list repo {repo_name}')
		assert results.rc == 0
		list_results = results.stdout

		# do a dump and compare against an expected output
		results = host.run('stack dump repo')
		assert results.rc == 0
		assert json.loads(results.stdout)['software'] == json.loads(expected_dumpfile.read_text())['software']

		# remove test data
		results = host.run(f'stack remove repo {repo_name}')
		assert results.rc == 0

		# verify clean state
		results = host.run(f'stack list repo {repo_name}')
		assert results.rc == 255
		assert results.stderr.startswith('error - ')

		# load expected dumpfile and compare against earlier listing
		stack_load(expected_dumpfile)

		results = host.run(f'stack list repo {repo_name}')
		assert results.rc == 0
		assert list_results == results.stdout

	def test_load_multiple_dumped_repos(self, host, stack_load, test_file, fake_os_sles, revert_etc):
		expected_dumpfile = Path(test_file('dump/multiple-repo.json')).resolve()

		repo_name1 = ADD_REPO_ARGUMENTS[0][0]
		repo_args1 = ' '.join(ADD_REPO_ARGUMENTS[0][1])
		repo_name2 = ADD_REPO_ARGUMENTS[1][0]
		repo_args2 = ' '.join(ADD_REPO_ARGUMENTS[1][1])

		# setup the test data using the first two repos from the dataset above
		for repo_name, repo_args in ((repo_name1, repo_args1), (repo_name2, repo_args2)):
			results = host.run(f'stack add repo {repo_name} {repo_args}')
			assert results.rc == 0

		# keep the stack list output for later comparison
		results = host.run(f'stack list repo {repo_name1} {repo_name2}')
		assert results.rc == 0
		list_results = results.stdout

		# do a dump and compare against an expected output
		results = host.run('stack dump repo')
		assert results.rc == 0
		assert json.loads(results.stdout)['software'] == json.loads(expected_dumpfile.read_text())['software']

		# remove test data
		results = host.run(f'stack remove repo {repo_name1} {repo_name2}')
		assert results.rc == 0

		# verify clean state
		for repo_name, repo_args in ((repo_name1, repo_args1), (repo_name2, repo_args2)):
			results = host.run(f'stack list repo {repo_name}')
			assert results.rc == 255
			assert results.stderr.startswith('error - ')

		# load expected dumpfile and compare against earlier listing
		stack_load(expected_dumpfile)

		results = host.run(f'stack list repo {repo_name1} {repo_name2}')
		assert results.rc == 0
		assert list_results == results.stdout

	def test_cart(self, host, revert_export_stack_carts):

		# test that dump software provides accurate cart information
		# add a test cart to the database
		results = host.run('stack add cart test')
		assert results.rc == 0

		# dump our software information
		results = host.run('stack dump cart')
		assert results.rc == 0
		dumped_data = json.loads(results.stdout)

		# check to make sure that our dump contains accurate cart information
		check = False
		for cart in dumped_data['software']['cart']:
			if cart['name'] == 'test':
				check = True
		assert check == True
