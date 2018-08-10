import pytest

class TestLoadJsonOs:

	"""
	Test that the load json os is able to load what dump os dumps
	"""

	def test_load_json_os(self, host):

		# add some os information so we have something to dump and load
		results = host.run('stack add os attr redhat attr=test value=test shadow=False')
		assert results.rc == 0
		results = host.run('stack add os route redhat address=192.168.0.0 gateway=192.168.0.1 netmask=255.255.255.0')
		assert results.rc == 0
		results = host.run('stack add os firewall redhat action=accept chain=input protocol=udp service=www network=private output-network=private rulename=ostest table=filter comment="test" flags="-m set"')
		assert results.rc == 0
		# the storage stuff is commented out for now, waiting for the storage fixes
#		results = host.run('stack add storage partition redhat device=test options="test option" size=1 mountpoint=test partid=1 type=ext4')
#		assert results.rc == 0
#		results = host.run('stack add storage controller redhat adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
#		assert results.rc == 0

		# dump the os data
		results = host.run('stack dump os')
		assert results.rc == 0
		initial_os_data = results.stdout.strip()

		#write the output to a file
		with open ('os.json', 'w+') as file:
			file.write(initial_os_data)

		# now we remove the information we just added to make sure that the load is effective
		results = host.run('stack remove os attr redhat attr=test')
		assert results.rc == 0
		results = host.run('stack remove os route redhat address=192.168.0.0')
		assert results.rc == 0
		results = host.run('stack remove os firewall redhat rulename=ostest')
		#
		# add storage stuff after the storage fix branch has been added
		#

		#reload the os json file
		results = host.run('stack load json os file=os.json')
		assert results.rc == 0

		# re-dump the data and check that nothing has changed
		results = host.run('stack dump os')
		assert results.rc == 0
		final_os_data = results.stdout.strip()

		# make sure that they are the same
		assert set(initial_os_data) == set(final_os_data)
