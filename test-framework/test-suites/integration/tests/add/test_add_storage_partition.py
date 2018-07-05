import pytest


class TestAddStoragePartitionBase:

	"""
	Test that we can successfully add an os level storage partition
	"""

	def test_add_storage_partition(self, host):

		# this should not work as it is now deprecated, scope is required
		results = host.run('stack add storage partition redhat device=test0 size=1 partid=1')
		assert results.rc != 1
		assert 'argument unexpected, please provide a scope:' in results.stderr


class TestAddStoragePartitionScopes():
	"""
	storage partition {name} {scope=string}  {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]
	appliance storage partition {name}   {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]
	host storage partition {name}   {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]
	os storage partition {name}   {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]"""

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_partition_scope_param(self, host):
		#this should work and have no errors
		result = host.run('stack add storage partition scope=global device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add storage partition backend scope=appliance device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add storage partition backend-0-0 scope=host device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add storage partition sles scope=os device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		host.run('stack add environment test')
		result = host.run('stack add storage partition test scope=environment device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	def test_add_storage_partition_multi(self, host):
		host.run('stack add host backend-0-0')
		host.run('stack add host backend-0-1')
		host.run('stack add host backend-0-2')
		result = host.run('stack add storage partition a:backend scope=host device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_partition_scope_verb(self, host):
		#this should work and have no errors
		result = host.run('stack add storage partition device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage partition backend device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add host storage partition backend-0-0 device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add os storage partition sles device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		host.run('stack add environment test')
		result = host.run('stack add environment storage partition test device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout


	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_partition_double_add_partid_negative(self, host):
		#the first ones should work fine, then error out on the 2nd add
		result = host.run('stack add storage partition scope=global device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage partition backend device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add host storage partition backend-0-0 device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add os storage partition sles device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout

		# 2nd add:
		result = host.run('stack add storage partition scope=global device=test0 size=1 partid=1')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage partition backend device=test0 size=1 partid=1')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add host storage partition backend-0-0 device=test0 size=1 partid=1')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add os storage partition sles device=test0 size=1 partid=1')
		assert result.rc != 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_add_storage_partition_double_add_mount_negative(self, host):
		#the first ones should work fine, then error out on the 2nd add
		result = host.run('stack add storage partition scope=global device=test0 size=1 partid=1 mountpoint=/')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage partition backend device=test0 size=1 partid=1 mountpoint=/')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add host storage partition backend-0-0 device=test0 size=1 partid=1 mountpoint=/')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack add os storage partition sles device=test0 size=1 partid=1 mountpoint=/')
		assert result.rc == 0
		assert '' == result.stdout
		host.run('stack add environment test')
		result = host.run('stack add environment storage partition test device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout


		# 2nd add:
		result = host.run('stack add storage partition scope=global device=test0 size=1 partid=2 mountpoint=/')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add appliance storage partition backend device=test0 size=1 partid=2 mountpoint=/')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add host storage partition backend-0-0 device=test0 size=1 partid=2 mountpoint=/')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add os storage partition sles device=test0 size=1 partid=2 mountpoint=/')
		assert result.rc != 0
		assert '' == result.stdout
		result = host.run('stack add environment storage partition test device=test0 size=1 partid=1')
		assert result.rc != 0
		assert '' == result.stdout

	@pytest.mark.usefixtures("revert_database")
	def test_add_storage_partition_scopes_negative(self, host):
		#these shouldn't work
		accepted_scopes = ['global', 'os', 'appliance', 'host']
		for scope in accepted_scopes:
			if scope != 'global':
				result = host.run('stack add storage partition scope=%s' % scope)
				assert result.rc == 255
				assert 'error - "device" parameter is required' in result.stderr
				result = host.run('stack add storage partition scope=%s device=vda' % scope)
				assert result.rc == 255
				assert 'error - "size" parameter is required' in result.stderr
				result = host.run('stack add storage partition scope=%s device=vda size=0' % scope)
				assert result.rc == 255
				assert '"%s name" argument is required' % scope in result.stderr
				result = host.run('stack add storage partition scope=%s device=vda size=0 test' % scope)
				assert result.rc == 255
				if scope == 'host':
					assert 'error - cannot resolve host "test"' in str(result.stderr).lower()
				else:
					assert '"test" argument is not a valid %s' % scope in str(result.stderr).lower()
			else:
				result = host.run('stack add storage partition scope=%s' % scope)
				assert result.rc == 255
				assert 'error - "device" parameter is required' in result.stderr
				result = host.run('stack add storage partition scope=%s device=vda' % scope)
				assert result.rc == 255
				assert 'error - "size" parameter is required' in result.stderr
