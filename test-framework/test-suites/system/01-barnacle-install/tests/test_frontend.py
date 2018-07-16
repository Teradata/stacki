import pytest


def test_frontend_stack_report_system(host):
	"Simple sanity test that a frontend is up and running"

	# We have to run sudo ourselves because stack report system needs to be ran
	# as an login shell for its tests to pass
	cmd = host.run("sudo -i stack report system")

	assert cmd.rc == 0

def test_stack_command_displays_usage_strings(host):
	"""
	The command line attempts to recursively import the command directory to find code to run
	or help text.  This will fail if it encounters a file which is not a valid python file.
	"""
	# A fix is in place to ignore files/directories that start with '.', such as those created by
	# pytest (and thus stack report system), so test that too.
	cmd = host.run("sudo -i stack report system")
	assert cmd.rc == 0

	# a .pytest_cache directory now exists in the command line path

	cmd = host.run("sudo -i stack")
	assert cmd.rc == 0
	assert 'import failed (missing or bad file)' not in cmd.stdout

def test_daily_db_backup_cronjob_script(host):
	"A cronjob is installed that backs up the mysql database daily, ensure this continues to work"

	# run the backup script directly
	cmd = host.run("sudo -i bash /etc/cron.daily/backup-cluster-db")
	assert cmd.rc == 0

	# check the backup now exists...
	backupfilename = '/var/db/mysql-backup-cluster'
	assert host.file(backupfilename).exists
	assert host.file(backupfilename).size != 0

	# remove a known host from the database
	cmd = host.run('sudo -i stack list host backend-0-0')
	assert cmd.rc == 0
	cmd = host.run('sudo -i stack remove host backend-0-0')
	assert cmd.rc == 0
	# host should be gone
	cmd = host.run('sudo -i stack list host backend-0-0')
	assert cmd.rc != 0

	# remove a known user from django auth
	cmd = host.run('sudo -i stack list api user output-format=json')
	assert cmd.rc == 0
	assert '"username": "admin",' in cmd.stdout
	cmd = host.run('sudo -i stack remove api user admin')
	assert cmd.rc == 0
	# user should be gone
	cmd = host.run('sudo -i stack list api user output-format=json')
	assert '"username": "admin",' not in cmd.stdout
	cmd = host.run('sudo -i stack remove api user admin')
	assert cmd.rc != 0

	# now restore the database and verify existance of removed host and api user
	cmd = host.run("sudo -i bash /var/db/restore-stacki-database.sh")
	assert cmd.rc == 0
	cmd = host.run("sudo -i stack list host backend-0-0")
	assert cmd.rc == 0
	cmd = host.run('sudo -i stack list api user output-format=json')
	assert cmd.rc == 0
	assert '"username": "admin",' in cmd.stdout

@pytest.mark.parametrize("backend", ("backend-0-0", "backend-0-1"))
def test_frontend_ssh_to_backends(host, backend):
	"Test that the frontend can SSH to its backends"

	cmd = host.run("sudo -i ssh {} hostname".format(backend))
	
	assert cmd.rc == 0
	assert cmd.stdout.strip().split('.')[0] == backend

def test_default_appliances_have_sane_attributes(host):
	"Test that default appliances are created with expected attrs"

	expected_output = host.run("cat /export/test-files/default_appliance_attrs_output.json")

	cmd = host.run("sudo -i stack list appliance attr output-format=json")

	assert cmd.rc == 0
	assert cmd.stdout.strip() == expected_output.stdout.strip()
