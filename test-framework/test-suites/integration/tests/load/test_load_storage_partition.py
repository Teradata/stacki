import pytest

@pytest.mark.usefixtures("revert_database")
class TestLoadStoragePartition:

	# add other csv's here after they are fixed, or better yet make this a glob
	STORAGE_SPREADSHEETS = ['lvm-complex']

	@pytest.mark.usefixtures("add_host")
	@pytest.mark.parametrize("csvfile", STORAGE_SPREADSHEETS)
	def test_load_storage_partition(self, host, csvfile):
		# get filename
		out = host.run('stack report version').stdout
		dirn = '/opt/stack/share/examples/spreadsheets/'
		fi = dirn + 'stacki-' + out.strip() + '-partition-' + csvfile + '.csv'

		# check that it has no partition info by default
		result = host.run('stack list host storage partition backend-0-0')
		assert result.rc == 0
		assert result.stdout == ''

		# load the partition file
		result = host.run(f'stack load storage partition file={fi}')
		assert result.rc == 0

		# check that it has partition info
		result = host.run('stack list host storage partition backend-0-0')
		assert result.rc == 0
		assert result.stdout != ''


STORAGE_SPREADSHEETS = ['multi_teradata_global', 'multi_teradata_backend', 'scopes']

@pytest.mark.usefixtures("revert_database")
@pytest.mark.usefixtures("add_host")
@pytest.mark.parametrize("csvfile", STORAGE_SPREADSHEETS)
def test_load_files_storage_partition(host, csvfile):
	# get filename
	host.run('stack add host backend-0-1')
	host.run('stack add environment test')
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
	if 'scopes' in input_file:
		for scope in ['os', 'host', 'appliance', 'environment']:
			result = host.run('stack list %s storage partition' % scope)
			assert result.rc == 0
			assert '%s' % scope in result.stdout
	assert result.stderr == ''

	# load the partition file again, this should be repeatable
	result = host.run('stack load storage partition file=%s' % input_file)
	assert result.rc == 0

	# check that it has partition info
	result = host.run('stack list storage partition %s' % hostname)
	assert result.rc == 0
	assert 'sda' in result.stdout
	if 'scopes' in input_file:
		for scope in ['os', 'host', 'appliance', 'environment']:
			result = host.run('stack list %s storage partition' % scope)
			assert result.rc == 0
			assert '%s' % scope in result.stdout
	assert result.stderr == ''
