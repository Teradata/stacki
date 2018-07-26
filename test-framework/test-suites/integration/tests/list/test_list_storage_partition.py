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

		# # make sure that we are able to list the entry we just added
		# results = host.run('stack list storage partition redhat')
		# assert 'redhat' in str(results.stdout)
		#
		# # this should not work because the size parameter is required
		# results = host.run('stack add storage partition redhat device=test0')
		# assert results.rc != 0
		#
		# # this should not work because 'blah' is not a valid scope
		# results = host.run('stack add storage partition blah  device=test0 size=1 partid=1')
		# assert results.rc != 0

class TestAddStoragePartitionScopes():
	"""
	storage partition {name} {scope=string}  {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]
	appliance storage partition {name}   {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]
	host storage partition {name}   {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]
	os storage partition {name}   {device=string} {options=string} {size=int} [mountpoint=string] [partid=int] [type=string]"""

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_list_storage_partition_scope_param(self, host):
		#this should work and have no errors
		result = host.run('stack add storage partition scope=global device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list storage partition scope=global ')
		assert result.rc == 0
		assert 'global' in result.stdout

		result = host.run('stack add storage partition backend scope=appliance device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list storage partition scope=appliance backend')
		assert result.rc == 0
		assert 'appliance' in result.stdout
		assert 'backend' in result.stdout

		result = host.run('stack add storage partition backend-0-0 scope=host device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list storage partition scope=host backend-0-0')
		assert result.rc == 0
		assert 'host' in result.stdout
		assert 'backend-0-0' in result.stdout


		result = host.run('stack add storage partition sles scope=os device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list storage partition scope=os sles')
		assert result.rc == 0
		assert 'os' in result.stdout
		assert 'sles' in result.stdout


		host.run('stack add environment test')
		result = host.run('stack add storage partition test scope=environment device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list storage partition scope=environment test')
		assert result.rc == 0
		assert 'environment' in result.stdout
		assert 'test ' in result.stdout

	@pytest.mark.usefixtures("revert_database")
	def test_list_storage_partition_multi(self, host):
		host.run('stack add host backend-0-0')
		host.run('stack add host backend-0-1')
		host.run('stack add host backend-0-2')
		result = host.run('stack add storage partition a:backend scope=host device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list host storage partition a:backend')
		assert result.rc == 0
		assert 'host' in result.stdout
		assert 'backend-0-0' in result.stdout
		assert 'backend-0-1' in result.stdout
		assert 'backend-0-2' in result.stdout

	@pytest.mark.usefixtures("revert_database")
	@pytest.mark.usefixtures("add_host")
	def test_list_storage_partition_scope_verb(self, host):
		#this should work and have no errors
		result = host.run('stack add storage partition device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list storage partition scope=global ')
		assert result.rc == 0
		assert 'global' in result.stdout

		result = host.run('stack add appliance storage partition backend device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list appliance storage partition backend')
		assert result.rc == 0
		assert 'appliance' in result.stdout
		assert 'backend' in result.stdout

		result = host.run('stack add host storage partition backend-0-0 device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list host storage partition')
		assert result.rc == 0
		assert 'host' in result.stdout
		assert 'backend-0-0' in result.stdout

		result = host.run('stack add os storage partition sles device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list os storage partition sles')
		assert result.rc == 0
		assert 'os' in result.stdout
		assert 'sles' in result.stdout

		host.run('stack add environment test')
		result = host.run('stack add environment storage partition test device=test0 size=1 partid=1')
		assert result.rc == 0
		assert '' == result.stdout
		result = host.run('stack list environment storage partition backend')
		assert result.rc == 0
		assert 'environment' in result.stdout
		assert 'test ' in result.stdout


	@pytest.mark.usefixtures("revert_database")
	def test_list_storage_partition_scopes_negative(self, host):
		#these shouldn't work
		accepted_scopes = ['os', 'appliance', 'host']
		for scope in accepted_scopes:
			if scope != 'global':
				result = host.run('stack list storage partition scope=%s test' % scope)
				assert result.rc == 255
				if scope == 'host':
					assert 'error - cannot resolve host "test"' in str(result.stderr).lower()
				else:
					assert '"test" argument is not a valid %s' % scope in str(result.stderr).lower()
