class TestAddStorageController:
	"""
	Test that we can successfully add an os level storage controller
	"""

	def test_single_arg(self, host):
		#this should work and have no errors
		results = host.run('stack add storage controller redhat adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
		assert results.rc == 0

		#make sure that we are able to list the entry we just added
		results = host.run('stack list storage controller redhat')
		assert 'redhat' in str(results.stdout)

		#this should not work because 'blah' is not a valid scope
		results = host.run('stack add storage controller blah adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
		assert results.rc != 0
