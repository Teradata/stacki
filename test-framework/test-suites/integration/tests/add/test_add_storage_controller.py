import pytest


class TestAddStorageControllerBase:
	"""
	A very basic test.
	Most of which was removed due to scope updates which required the more extensive tests below.
	"""
	def test_default_list_and_add_storage_controller_blah(self, host):
		"""Check that global defaul exists already in the database. Then input bad data."""

		# There is a default raid0 config existing:
		results = host.run('stack list storage controller')
		assert 2 == len(results.stdout.splitlines())

		# This should not work because 'blah' is not a valid scope
		results = host.run('stack add storage controller blah adapter=1 arrayid=2 enclosure=3 raidlevel=4 slot=5')
		assert results.rc != 0


class TestAddStorageControllerScopes:
	"""
	storage controller {name} {scope=string} [adapter=int] [arrayid=string] [enclosure=int] [hotspare=int]
	 [raidlevel=int] [slot=int]
	"""
	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_controller_scope_param(self, host):
		"""This should work and have no errors. """
		result = host.run('stack add storage controller scope=global adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add storage controller backend scope=appliance adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add storage controller backend-0-0 scope=host adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add storage controller sles scope=os adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		host.run('stack add environment test')
		result = host.run('stack add storage controller test scope=environment adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	def test_add_storage_controller_multi(self, host):
		"""Add controller information for multiple backends."""
		host.run('stack add host backend-0-0')
		host.run('stack add host backend-0-1')
		host.run('stack add host backend-0-2')
		result = host.run('stack add storage controller a:backend scope=host adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_controller_scope_verb(self, host):
		"""This should work and have no errors. """
		result = host.run('stack add storage controller adapter=1 arrayid=1 enclosure=1 hotspare=0 raidlevel=1 '
		                  'slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage controller backend adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add host storage controller backend-0-0 adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add os storage controller sles adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		host.run('stack add environment test')
		result = host.run('stack add environment storage controller test adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_controller_double_add_partid_negative(self, host):
		"""the first ones should work fine, then error out on the 2nd add."""
		result = host.run('stack add storage controller scope=global adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage controller backend adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add host storage controller backend-0-0 adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add os storage controller sles adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout

		# 2nd add:
		result = host.run('stack add storage controller scope=global adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage controller backend adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add host storage controller backend-0-0 adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add os storage controller sles adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_controller_double_add_mount_negative(self, host):
		"""The first ones should work fine, then error out on the 2nd add."""

		result = host.run('stack add storage controller scope=global adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage controller backend adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add host storage controller backend-0-0 adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add os storage controller sles adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout
		host.run('stack add environment test')
		result = host.run('stack add environment storage controller test adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc == 0
		assert '' == result.stdout

		# 2nd add:
		result = host.run('stack add storage controller scope=global adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage controller backend adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add host storage controller backend-0-0 adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add os storage controller sles adapter=1 arrayid=1 enclosure=1 hotspare=0 '
		                  'raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add environment storage controller test adapter=1 arrayid=1 enclosure=1 '
		                  'hotspare=0 raidlevel=1 slot=1,2')
		assert result.rc != 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	def test_add_storage_controller_scopes_negative(self, host):
		"""these shouldn't work"""
		accepted_scopes = ['global', 'os', 'appliance', 'host']
		for scope in accepted_scopes:
			result = host.run('stack add storage controller scope=%s' % scope)
			assert result.rc == 255
			assert 'error - "arrayid" parameter is required' in result.stderr
			if scope != 'global':
				result = host.run('stack add storage controller scope=%s arrayid=1 slot=1' % scope)
				assert result.rc == 255
				assert '"%s name" argument is required' % scope in result.stderr
				result = host.run('stack add storage controller scope=%s arrayid=1 slot=1 test' % scope)
				assert result.rc == 255
				if scope == 'host':
					assert 'error - cannot resolve host "test"' in str(result.stderr).lower()
				else:
					assert '"test" argument is not a valid %s' % scope in str(result.stderr).lower()
			else:
				result = host.run('stack add storage controller scope=%s arrayid=1' % scope)
				assert result.rc == 255
				assert 'error - "slot" or "hotspare" parameter is required' in result.stderr
				result = host.run('stack add storage controller scope=%s arrayid=1 slot=1' % scope)
				assert result.rc == 255
				assert 'error - "raidlevel" parameter is required' in result.stderr
