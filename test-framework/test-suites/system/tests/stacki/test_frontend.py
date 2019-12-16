import pytest
import json


def test_stack_command_displays_usage_strings(host):
	"""
	The command line attempts to recursively import the command directory to find code to run
	or help text.  This will fail if it encounters a file which is not a valid python file.
	"""

	# A fix is in place to ignore files/directories that start with '.', such as those created by
	# pytest (and thus stack report system), so test that too.
	cmd = host.run("stack report system")
	assert cmd.rc == 0

	# a .pytest_cache directory now exists in the command line path

	cmd = host.run("stack")
	assert cmd.rc == 0
	assert 'import failed (missing or bad file)' not in cmd.stdout

def test_daily_db_backup_cronjob_script(host):
	"A cronjob is installed that backs up the mysql database daily, ensure this continues to work"

	# run the backup script directly
	cmd = host.run("bash /etc/cron.daily/backup-cluster-db")
	assert cmd.rc == 0

	# check the backup now exists...
	backupfilename = '/var/db/mysql-backup-cluster'
	assert host.file(backupfilename).exists
	assert host.file(backupfilename).size != 0

	# remove a known host from the database
	cmd = host.run('stack list host backend-0-0')
	assert cmd.rc == 0
	cmd = host.run('stack remove host backend-0-0')
	assert cmd.rc == 0

	# host should be gone
	cmd = host.run('stack list host backend-0-0')
	assert cmd.rc != 0

	# remove a known user from django auth
	cmd = host.run('stack list api user output-format=json')
	assert cmd.rc == 0
	assert '"username": "admin",' in cmd.stdout
	cmd = host.run('stack remove api user admin')
	assert cmd.rc == 0

	# user should be gone
	cmd = host.run('stack list api user output-format=json')
	assert '"username": "admin",' not in cmd.stdout
	cmd = host.run('stack remove api user admin')
	assert cmd.rc != 0

	# now restore the database and verify existance of removed host and api user
	cmd = host.run("bash /var/db/restore-stacki-database.sh")
	assert cmd.rc == 0
	assert 'error' not in cmd.stdout.lower()
	assert 'error' not in cmd.stderr.lower()

	cmd = host.run("stack list host backend-0-0")
	assert cmd.rc == 0

	cmd = host.run('stack list api user output-format=json')
	assert cmd.rc == 0
	assert '"username": "admin",' in cmd.stdout

def test_default_appliances_have_sane_attributes(host, test_file):
	"Test that default appliances are created with expected attrs"

	with open(test_file('default_appliance_attrs_output.json')) as f:
		expected_result = json.load(f)

	cmd = host.run("stack list appliance attr output-format=json")
	assert cmd.rc == 0

	actual_result = json.loads(cmd.stdout)
	for attribute in expected_result:
		assert attribute in actual_result

def test_packages_have_hashes(host):
	results = host.run('rpm -qa "stack-*" --queryformat "%{VENDOR} %{NAME} %{VCS}\n"')
	assert results.rc == 0
	assert results.stdout.strip() != ''
	for pkgline in results.stdout.splitlines():
		assert pkgline.split()[-1] != '(none)'

def test_report_system(host):
	"""Make sure report system doesn't report any errors."""
	cmd = host.run("stack report system")
	assert cmd.rc == 0

def test_ansible(host, test_file):
	"""Test that ansible can run on the frontend and talk to the backends."""
	# Lay down the ansible inventory file on the frontend.
	cmd = host.run("stack report ansible | stack report script | bash")
	assert cmd.rc == 0
	# Run an ansible playbook that sshes into each node.
	cmd = host.run(f"ansible-playbook --verbose {test_file('test_ansible.yml')}")
	assert cmd.rc == 0
	# The system test suite currently stands up 3 backends, so expect 3
	# echo outputs in the stdout.
	assert cmd.stdout.count('"stdout": "hello ansible"') == 3

def test_foundation_python(host):
	results = host.run("/opt/stack/bin/python3 -c 'import _sqlite3'")
	assert results.rc == 0
	assert results.stdout.strip() == ''
	assert results.stderr.strip() == ''
