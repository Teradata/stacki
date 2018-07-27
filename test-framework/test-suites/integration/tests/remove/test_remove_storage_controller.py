import os
import subprocess
import pytest
import tempfile

STORAGE_SPREADSHEETS = ['backend', 'global']


def check_controller_output(host, hostname, dirn, csvfile, output_num):
	# check that it has controller info
	stack_output_file = tempfile.NamedTemporaryFile(delete=True)
	result = host.run('stack list storage controller %s > %s' % (hostname, stack_output_file.name))
	assert result.rc == 0
	assert result.stderr == ''
	output_file = dirn + csvfile + '_output_' + str(output_num) + '.csv'
	with open(output_file) as test_file:
		test_lines = test_file.readlines()

	with open(stack_output_file.name) as stack_file:
		stack_lines = stack_file.readlines()
	print(test_lines)
	print(stack_lines)
	assert len(test_lines) == len(stack_lines)
	for i in range(len(test_lines)):
		assert test_lines[i].strip() == stack_lines[i].strip()


@pytest.mark.usefixtures("revert_database")
@pytest.mark.usefixtures("add_host")
@pytest.mark.parametrize("csvfile", STORAGE_SPREADSHEETS)
def test_remove_storage_controller(host, csvfile):
	# get filename

	result = host.run('stack add host backend-0-1')
	assert result.rc == 0
	assert result.stdout == ''

	dirn = '/export/test-files/load/storage_controller_'
	input_file = dirn + csvfile + '_input' + '.csv'

	if 'global' in input_file:
		hostname = ''
		# check that it has no controller info by default
		result = host.run('stack list storage controller %s' % hostname)
		assert result.rc == 0
		assert len(str(result.stdout).splitlines()) == 2
	else:
		hostname = 'scope=host backend-0-0'
		# check that it has no controller info by default
		result = host.run('stack list storage controller %s' % hostname)
		assert result.rc == 0
		assert result.stdout == ''

	# load the controller file
	result = host.run('stack load storage controller file=%s' % input_file)
	assert result.rc == 0
	# Check that everything was added:
	check_controller_output(host, hostname, dirn, csvfile, 0)

	# remove the controller info for a single slot and enclosure
	result = host.run('stack remove storage controller %s slot=8 enclosure=1' % hostname)
	assert result.rc == 0
	assert result.stderr == ''
	# Check that it is indeed removed
	check_controller_output(host, hostname, dirn, csvfile, 1)

	# remove the controller info for a single arrayid
	result = host.run('stack remove storage controller %s arrayid=2 slot="*"' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''
	# Check that it is indeed removed
	check_controller_output(host, hostname, dirn, csvfile, 2)

	# remove all the controller info
	result = host.run('stack remove storage controller %s enclosure="*" slot="*"' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''

	# check that it has no controller info again
	result = host.run('stack list storage controller %s' % hostname)
	assert result.rc == 0
	assert result.stdout == ''
	assert result.stderr == ''



@pytest.mark.usefixtures("revert_database")
def test_remove_host_plugin(host):

	for backend in ['backend-0-0', 'backend-0-1']:
		result = host.run('stack add host %s' % backend)
		assert result.rc == 0
		assert result.stdout == ''
		# check that it has no controller info by default
		result = host.run('stack list host storage controller  %s' % backend)
		assert result.rc == 0
		assert result.stdout == ''
		# add the controller info
		result = host.run('stack add host storage controller arrayid=1 slot=0 raidlevel=1 %s' % backend)
		assert result.rc == 0
		result = host.run('stack add host storage controller arrayid=1 slot=1 raidlevel=1 %s' % backend)
		assert result.rc == 0
		# check that something was added
		result = host.run('stack list host storage controller %s' % backend)
		assert result.rc == 0
		assert result.stdout != ''
	# Only remove one so that we can check it only removes that ones' controller info
	result = host.run('stack remove host backend-0-0')
	assert result.rc == 0
	assert result.stdout == ''

	# If plugins don't run the database has extra entries. Can't access this data with a stack command.
	result = host.run('mysql cluster -e "select count(scope) from storage_controller where scope=\'host\';"')
	assert result.rc == 0
	# Since we only removed 1 host we should still have the other host's 2 entrie
	assert 'count(scope)\n2\n' in result.stdout


@pytest.mark.usefixtures("revert_database")
def test_remove_appliance_plugin(host):

	for appliance in ['master', 'mistress']:
		result = host.run('stack add appliance %s' % appliance)
		assert result.rc == 0
		assert result.stdout == ''

		# check that it has no controller info by default
		result = host.run('stack list appliance storage controller %s' % appliance)
		assert result.rc == 0
		assert result.stdout == ''

		# add the controller info
		result = host.run('stack add appliance storage controller arrayid=1 slot=0 raidlevel=1 %s' % appliance)
		assert result.rc == 0
		result = host.run('stack add appliance storage controller arrayid=1 slot=1 raidlevel=1 %s' % appliance)
		assert result.rc == 0

		# check that something was added
		result = host.run('stack list appliance storage controller %s' % appliance)
		assert result.rc == 0
		assert result.stdout != ''

	result = host.run('stack remove appliance master')
	assert result.rc == 0
	assert result.stdout == ''

	# If plugins don't run the database has extra entries. Can't access this data with a stack command.
	result = host.run('mysql cluster -e "select count(scope) from storage_controller where scope=\'appliance\';"')
	assert result.rc == 0
	# Since we only removed 1 appliance we should still have the other appliance's 2 entrie
	assert 'count(scope)\n2\n' in result.stdout


@pytest.mark.usefixtures("revert_database")
def test_remove_environment_plugin(host):

	for environment in ['master', 'mistress']:
		result = host.run('stack add environment %s' % environment)
		assert result.rc == 0
		assert result.stdout == ''

		# check that it has no controller info by default
		result = host.run('stack list environment storage controller %s' % environment)
		assert result.rc == 0
		assert result.stdout == ''

		# add the controller info
		result = host.run('stack add environment storage controller arrayid=1 slot=0 raidlevel=1 %s' % environment)
		assert result.rc == 0
		result = host.run('stack add environment storage controller arrayid=1 slot=1 raidlevel=1 %s' % environment)
		assert result.rc == 0

		# check that something was added
		result = host.run('stack list environment storage controller %s' % environment)
		assert result.rc == 0
		assert result.stdout != ''

	result = host.run('stack remove environment master')
	assert result.rc == 0
	assert result.stdout == ''

	# If plugins don't run the database has extra entries. Can't access this data with a stack command.
	result = host.run('mysql cluster -e "select count(scope) from storage_controller where scope=\'environment\';"')
	assert result.rc == 0
	# Since we only removed 1 environment we should still have the other environment's 2 entrie
	assert 'count(scope)\n2\n' in result.stdout


@pytest.mark.usefixtures("revert_database")
def test_remove_os_plugin(host):

	for os in ['ubuntu', 'redhat']:
		# check that it has no controller info by default
		result = host.run('stack list os storage controller %s' % os)
		assert result.rc == 0
		assert result.stdout == ''

		# add the controller info
		result = host.run('stack add os storage controller arrayid=1 slot=0 raidlevel=1 %s' % os)
		assert result.rc == 0
		result = host.run('stack add os storage controller arrayid=1 slot=1 raidlevel=1 %s' % os)
		assert result.rc == 0

		# check that something was added
		result = host.run('stack list os storage controller %s' % os)
		assert result.rc == 0
		assert result.stdout != ''

	result = host.run('stack remove os ubuntu')
	assert result.rc == 0
	assert result.stdout == ''

	# If plugins don't run the database has extra entries. Can't access this data with a stack command.
	sql_cmd = """select count(scope) from storage_controller where scope='os';"""
	result = host.run('mysql cluster -e "%s"' % sql_cmd)
	assert result.rc == 0
	# Since we only removed 1 os we should still have the other os's 2 entries
	assert 'count(scope)\n2\n' in result.stdout

@pytest.mark.usefixtures("revert_database")
@pytest.mark.usefixtures("add_host")
def test_negative_remove_storage_controller(host):
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
	accepted_scopes = ['global', 'os', 'appliance', 'host', 'environment']

	# Provide extra data on global scope
	result = host.run('stack remove storage controller scope=global backend-0-0 slot=1')
	assert result.rc == 255
	assert 'argument unexpected' in result.stderr

	result = host.run('stack remove storage controller scope=garbage backend-0-0 slot=1')
	assert result.rc == 255
	assert '"scope" parameter must be one of the following:' in result.stderr

	for scope in accepted_scopes:
		if scope != 'global':
			result = host.run('stack remove storage controller scope=%s slot=1' % scope)
			assert result.rc == 255
			assert '"%s name" argument is required' % scope in result.stderr
		else:
			result = host.run('stack remove storage controller scope=%s' % scope)
			assert result.rc == 255
			assert '"slot" parameter is required' in result.stderr
