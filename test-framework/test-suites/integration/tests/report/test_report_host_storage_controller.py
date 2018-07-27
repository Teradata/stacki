import pytest

@pytest.mark.usefixtures("revert_database")
class TestLoadStorageController:

	# add other csv's here after they are fixed, or better yet make this a glob
	EX_STORAGE_SPREADSHEETS = ['hp-raid1+raid10', 'hp-raid10-advanced', 'hp-raid5', 'hp-raid50', 'hp-raid6',
	                        'hp-raid60', 'hp-ssd', 'megacli-raid10+raid50', 'megacli-raid5+raid6', 'megacli-raid60',
	                        'storcli-raid10+flags', 'storcli-raid10', 'storcli-raid5', 'storcli-raid50',
	                        'storcli-raid6', 'storcli-raid60', 'simpleraid1']

	@pytest.mark.usefixtures("add_host")
	@pytest.mark.parametrize("csvfile", EX_STORAGE_SPREADSHEETS)
	def test_example_load_report_storage_controller(self, host, csvfile):
		# get filename
		out = host.run('stack report version').stdout
		dirn = '/opt/stack/share/examples/spreadsheets/'
		fi = dirn + 'stacki-' + out.strip() + '-controller-' + csvfile + '.csv'

		# check that it has no controller info by default
		result = host.run('stack report host storage controller backend-0-0')
		assert result.rc == 0
		assert "{'scope': 'global', 'enclosure': None, 'adapter': None, 'slot': '*', 'raidlevel': '0', 'arrayid': " \
		       "'*', 'options': ''" in result.stdout

		# load the controller file
		result = host.run(f'stack load storage controller file={fi}')
		assert result.rc == 0

		# check that it has controller info
		result = host.run('stack report host storage controller backend-0-0')
		assert result.rc == 0
		assert result.stdout != ''


	@pytest.mark.usefixtures("add_host")
	def test_example_load_report_storage_controller(self, host):
		"""Set each environment for the host and check that they have the correct precedence."""
		scopes = ['global', 'os', 'appliance', 'environment', 'host']

		# Going down the list to make sure priority is applied correctly on report
		result = host.run('stack add environment master_node')
		assert result.rc == 0
		result = host.run('stack set host environment backend-0-0 environment=master_node')
		assert result.rc == 0
		previous_scope = 'global'
		for csvfile in scopes:
			dirn = '/export/test-files/load/storage_controller_'
			input_file = dirn + csvfile + '_input' + '.csv'

			# check that it has default controller info
			result = host.run('stack report host storage controller backend-0-0')
			assert result.rc == 0
			current_scope = "'scope': '%s'" % previous_scope
			assert current_scope in result.stdout

			# load the controller file
			result = host.run(f'stack load storage controller file={input_file} scope={csvfile}')
			assert result.rc == 0

			# check that it has controller info
			result = host.run('stack report host storage controller backend-0-0')
			assert result.rc == 0
			assert csvfile in result.stdout
			# The previous scope is needed to check that it took correctly,
			# and then was overwritten by a higher priority
			previous_scope = csvfile