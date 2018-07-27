import pytest

STORAGE_SPREADSHEETS = ['multi_teradata_global', 'multi_teradata_backend']

@pytest.mark.usefixtures("revert_database")
@pytest.mark.usefixtures("add_host")
@pytest.mark.parametrize("csvfile", STORAGE_SPREADSHEETS)
def test_remove_storage_partition(host, csvfile):
	# get filename
	dirn = '/export/test-files/load/storage_partition_'
	input_file = dirn + csvfile + '_input' + '.csv'

	if 'global' in input_file:
		hostname = ''
	else:
		hostname = 'scope=host backend-0-0'
	# check that it has no partition info by default
	result = host.run('stack list storage partition %s' % hostname)
	assert result.rc == 0
	assert result.stdout == ''

	# load the partition file
	result = host.run('stack load storage partition file=%s' % input_file)
	assert result.rc == 0

	# check that it has partition info
	result = host.run('stack list storage partition %s' % hostname)
	assert result.rc == 0
	assert 'sda' in result.stdout
	assert 'sdb' in result.stdout
	assert '/var/opt/teradata' in result.stdout
	assert result.stderr == ''

	# remove the partition info for a single device
	result = host.run('stack remove storage partition %s device=sdb' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''
	# Check that it is indeed removed
	result = host.run('stack list storage partition %s' % hostname)
	assert result.rc == 0
	assert 'sda' in result.stdout
	assert 'sdb' not in result.stdout

	# remove the partition info for a single mountpoint
	result = host.run('stack remove storage partition %s mountpoint="/var/opt/teradata"' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''
	# Check that it is indeed removed
	result = host.run('stack list storage partition %s' % hostname)
	assert result.rc == 0
	assert '/var/opt/teradata' not in result.stdout

	# remove all the partition info
	result = host.run('stack remove storage partition %s device="*"' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''

	# check that it has no partition info again
	result = host.run('stack list storage partition %s' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''


def test_remove_scope_storage_partition_blank_argument(host):
	"""Test all the scopes error out on blank argument input."""
	result = host.run('stack remove host storage partition device="*"')
	assert result.rc != 0
	assert result.stdout == ''
	assert 'argument is required' in result.stderr
	assert '"host name" argument is required' in result.stderr

	result = host.run('stack remove os storage partition device="*"')
	assert result.rc != 0
	assert result.stdout == ''
	assert '"os name" argument is required' in result.stderr

	result = host.run('stack remove appliance storage partition device="*"')
	assert result.rc != 0
	assert result.stdout == ''
	assert '"appliance name" argument is required' in result.stderr


@pytest.mark.usefixtures("revert_database")
@pytest.mark.usefixtures("add_host")
def test_negative_remove_storage_partition(host):
	"""
	Trying to hit the below exceptions. The order is important as it is contextual to the attempted input.

		if scope not in accepted_scopes:
			raise ParamValue(self, '%s' % params, 'one of the following: %s' % accepted_scopes )
		elif scope == 'global' and len(args) >= 1:
			raise ArgError(self, '%s' % args, 'unexpected, please provide a scope: %s' % accepted_scopes)
		elif scope == 'global' and (device is None and mountpoint is None):
			raise ParamRequired(self, 'device OR mountpoint')
		elif scope != 'global' and len(args) < 1:
			raise ArgRequired(self, '%s name' % scope)
	"""
	accepted_scopes = ['global', 'os', 'appliance', 'host']

	# Provide extra data on global scope
	result = host.run('stack remove storage partition scope=global backend-0-0 device=sda')
	assert result.rc == 255
	assert 'argument unexpected, please provide a scope:' in result.stderr

	result = host.run('stack remove storage partition scope=garbage backend-0-0 device=sda')
	assert result.rc == 255
	assert '"scope" parameter must be one of the following:' in result.stderr

	for scope in accepted_scopes:
		result = host.run('stack remove storage partition scope=%s' % scope)
		assert result.rc == 255
		assert 'error - "device" or "mountpoint" parameter is required' in result.stderr
