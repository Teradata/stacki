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
		result = host.run('stack list storage partition backend-0-0')
		assert result.rc == 0
		assert result.stdout == ''

		# load the partition file
		result = host.run(f'stack load storage partition file={fi}')
		assert result.rc == 0

		# check that it has partition info
		result = host.run('stack list storage partition backend-0-0')
		assert result.rc == 0
		assert result.stdout != ''
