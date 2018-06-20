import os
import shutil
import subprocess
import tempfile

import pytest


@pytest.fixture(scope="session")
def dump_mysql():
	# Create a temp file and open it for the subprocess command
	file_fd, file_path = tempfile.mkstemp(suffix=".sql")
	file_obj = os.fdopen(file_fd, mode="w")

	# Dump the initial Stacki DB into an SQL file, to restore from
	# after each test
	if os.path.exists("/opt/stack/etc/root.my.cnf"):
		subprocess.run([
			"mysqldump",
			"--defaults-file=/opt/stack/etc/root.my.cnf",
			"--lock-all-tables",
			"--add-drop-database",
			"--databases",
			"cluster"
		], stdout=file_obj, check=True)
	else:
		subprocess.run([
			"mysqldump",
			"--lock-all-tables",
			"--add-drop-database",
			"--databases",
			"cluster"
		], stdout=file_obj, check=True)
	
	# Close the file
	file_obj.close()
	
	# Done with the set up, yield our SQL file path
	yield file_path

	# Remove the SQL file
	os.remove(file_path)

@pytest.fixture
def revert_database(dump_mysql):
	# Don't need to do anything in the set up
	yield

	# Load a fresh database after each test
	with open(dump_mysql) as sql:
		if os.path.exists("/opt/stack/etc/root.my.cnf"):
			subprocess.run([
				"mysql",
				"--defaults-file=/opt/stack/etc/root.my.cnf"
			], stdin=sql, check=True)
		else:
			subprocess.run("mysql", stdin=sql, check=True)

@pytest.fixture
def revert_filesystem():
	# The paths to capture and revert changes to
	paths = (
		"/etc",
		"/export/stack",
		"/tftpboot"
	)

	# Unmount any existing overlay directories
	with open("/proc/mounts", "r") as mounts:
		# Create a tuple of lines because /proc/mounts will change
		# as we unmount things
		for mount in tuple(mounts):
			if mount.startswith("overlay_"):
				subprocess.run(
					["umount", mount.split()[0]],
					check=True
				)
	
	# Make sure the overlay root is clean
	if os.path.exists("/overlay"):
		shutil.rmtree("/overlay")

	for ndx, path in enumerate(paths):
		# Make the overlay directories
		overlay_dirs = {
			"lowerdir": path,
			"upperdir": os.path.join("/overlay", path[1:], "upper"),
			"workdir": os.path.join("/overlay", path[1:], "work")
		}

		os.makedirs(overlay_dirs['upperdir'])
		os.makedirs(overlay_dirs['workdir'])
	
		# Mount the overlays
		subprocess.run([
			"mount",
			"-t", "overlay",
			f"overlay_{ndx}",
			"-o", ",".join(f"{k}={v}" for k, v in overlay_dirs.items()),
			path
		], check=True)

@pytest.fixture
def revert_discovery():
	# Nothing to do in set up
	yield

	# Make sure discovery is turned off, in case a test failed. We get
	# four tries to actually shutdown the daemon
	for _ in range(4):
		result = subprocess.run(
			["stack", "disable", "discovery"],
			stdout=subprocess.PIPE,
			encoding="utf-8",
			check=True
		)

		# Make sure we were actually able to shutdown any daemons.
		if result.returncode == 0 and "Warning:" not in result.stdout:
			break
	else:
		# Fail the test if the daemon isn't behaving
		pytest.fail("Couldn't shut down discovery daemon")

	# Blow away the log file
	if os.path.exists("/var/log/stack-discovery.log"):
		os.remove("/var/log/stack-discovery.log")

@pytest.fixture
def add_host(hostname='backend-0-0', rack='1', rank='1', appliance='backend'):
	cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance={appliance}'
	result = subprocess.run(cmd.split())
	if result.returncode != 0:
		pytest.fail('unable to add a dummy host')

	yield

@pytest.fixture
def add_host_with_interface(hostname='backend-0-0', rack='1', rank='1', appliance='backend', interface='eth0'):
	cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance={appliance}'
	result = subprocess.run(cmd.split())
	if result.returncode != 0:
		pytest.fail('unable to add a dummy host')

	cmd = f'stack add host interface {hostname} interface={interface}'
	result = subprocess.run(cmd.split())
	if result.returncode != 0:
		pytest.fail('unable to add a dummy interface')

	yield

