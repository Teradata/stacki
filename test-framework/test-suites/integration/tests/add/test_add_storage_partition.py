import pytest


class TestAddStorageController:

	"""
	Test that we can successfully add an os level storage partition
	"""

	def test_add_storage_partition(self, host):

		#this should work and have no errors
		results = host.run('stack add storage partition redhat device=test0 size=1 partid=1')
		assert results.rc == 0

		#make sure that we are able to list the entry we just added
		results = host.run('stack list storage partition redhat')
		assert 'redhat' in str(results.stdout)

		#this should not work because the size parameter is required
		results = host.run('stack add storage partition redhat  device=test0')
		assert results.rc != 0

		#this should not work because 'blah' is not a valid scope
		results = host.run('stack add storage partition blah  device=test0 size=1 partid=1')
		assert results.rc != 0
