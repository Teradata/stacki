from contextlib import contextmanager
import glob
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import time

import pytest
from redis import StrictRedis


# Everything in "fixures" gets loaded
pytest_plugins = [
	f"fixtures.{p.stem}" for p in Path(__file__).parent.glob('fixtures/*.py')
	if p.stem != '__init__'
]

def pytest_addoption(parser):
	parser.addoption(
		"--audit", action="store_true", help="audit filesystem changes"
	)

class FakeWorkerID(object):
	@pytest.fixture(scope="session")
	def worker_id(self):
		return 'master'

def pytest_configure(config):
	# Are we auditing filesystem changes?
	if config.getoption("--audit"):
		filesystem_revert_fixtures = [
			"revert_etc",
			"revert_export_stack_carts",
			"revert_export_stack_pallets"
		]

		for fixture in filesystem_revert_fixtures:
			# Enable the revert filesystem fixture for every test
			config.addinivalue_line("usefixtures", fixture)

			# Make sure the log file doesn't exist
			if os.path.exists(f"/export/reports/{fixture}.log"):
				os.remove(f"/export/reports/{fixture}.log")

	# Make sure the debug log doesn't exist
	if os.path.exists("/export/reports/debug.log"):
		os.remove("/export/reports/debug.log")

	# If we don't have xdist, we need to fake the worker_id fixture
	if not config.pluginmanager.hasplugin('xdist'):
		config.pluginmanager.register(FakeWorkerID())

@pytest.fixture(scope="session")
def redis():
	yield StrictRedis(host='localhost')

@pytest.fixture
def debug_log(redis, request, worker_id):
	def _inner(message):
		with redis.lock("pytest_debug_log"):
			with open("/export/reports/debug.log", "a") as f:
				f.write(f"[{worker_id}] {request.node.nodeid} {message}\n")

	return _inner

@pytest.fixture(scope="session")
def dump_mysql(worker_id):
	# Create a temp file and open it for the subprocess command
	file_fd, file_path = tempfile.mkstemp(suffix=".sql")
	file_obj = os.fdopen(file_fd, mode="w")

	# Put drop database commands at the front of the SQL restore file
	file_obj.write("DROP DATABASE IF EXISTS `shadow`;\n")
	file_obj.write("DROP DATABASE IF EXISTS `cluster`;\n\n")
	file_obj.write("DROP DATABASE IF EXISTS `django`;\n\n")
	file_obj.flush()
	os.fsync(file_fd)

	# Dump the initial Stacki DB into an SQL file, to restore from after each test
	subprocess.run([
		"mysqldump", "--opt", "--databases", "cluster", "shadow", "django"
	], stdout=file_obj, check=True)

	# Close the file
	file_obj.flush()
	os.fsync(file_fd)
	file_obj.close()

	if worker_id != 'master':
		# Now replace the database names with our process specific ones
		subprocess.run(['sed', '-i', f's|`cluster`|`cluster{worker_id}`|g', file_path], check=True)
		subprocess.run(['sed', '-i', f's|`shadow`|`shadow{worker_id}`|g', file_path], check=True)

		# Load up the new process specific dbs
		with open(file_path) as sql:
			subprocess.run("mysql", stdin=sql, check=True)

		subprocess.run([
			'mysql', '-e', f'GRANT ALL ON `cluster{worker_id}`.* to apache@localhost'
		], check=True)

		subprocess.run([
			'mysql', '-e', f'GRANT ALL ON `shadow{worker_id}`.* to apache@localhost'
		], check=True)

		subprocess.run([
			'mysql', '-e', f"GRANT ALL ON `cluster{worker_id}`.* to ''@'localhost'"
		], check=True)

	# Done with the set up, yield our SQL file path
	yield file_path

	# Remove the SQL file
	os.remove(file_path)

	if worker_id != 'master':
		# Drop our process specific dbs
		subprocess.run(['mysql', '-e', f'DROP DATABASE `shadow{worker_id}`'], check=True)
		subprocess.run(['mysql', '-e', f'DROP DATABASE `cluster{worker_id}`'], check=True)

@pytest.fixture
def process_count(redis, request):
	# Pause this worker process if the exclusive lock is taken
	with redis.lock("pytest_exclusive_lock"):
		pass

	# We only increment the count if we aren't an exclusive process
	if "exclusive_lock" not in request.fixturenames:
		redis.incr("pytest_process_count")

	yield

	redis.decr("pytest_process_count")

@pytest.fixture
def exclusive_lock(redis):
	with redis.lock("pytest_exclusive_lock"):
		# Safe to increment the process count, now that we have the lock
		redis.incr("pytest_process_count")

		# Wait for all the other worker processes to run
		while(int(redis.get("pytest_process_count")) != 1):
			time.sleep(0.2)

		yield

@pytest.fixture
def set_host_interface(add_host_with_interface):
	result = subprocess.run(
		["stack", "list", "network", "private", "output-format=json"],
		stdout=subprocess.PIPE,
		encoding="utf-8",
		check=True
	)

	o = json.loads(result.stdout)
	addr = o[0]["address"]
	mask = o[0]["mask"]

	result = subprocess.run(
		["stack", "list", "host", "a:backend", "output-format=json"],
		stdout=subprocess.PIPE,
		encoding="utf-8",
		check=True
	)
	o = json.loads(result.stdout)
	hostname = o[0]["host"]

	result = subprocess.run(
		["stack", "list", "host", "interface", "output-format=json"],
		stdout=subprocess.PIPE,
		encoding="utf-8",
		check=True
	)

	o = json.loads(result.stdout)
	ip_list = []
	interface = None

	for line in o:
		if line['host'] == hostname:
			interface = line['interface']

		# Make list of IP addresses
		if line['ip']:
			ip_list.append(line['ip'])

	result = {
		'hostname' : hostname,
		'net_addr' : addr,
		'net_mask' : mask,
		'interface': interface,
		'ip_list'  : ip_list
	}

	return result

@pytest.fixture(scope="session")
def host_os():
	if os.path.exists('/etc/SuSE-release'):
		return 'sles'

	return 'redhat'

@pytest.fixture
def invalid_host():
	return 'invalid-{:04x}'.format(random.randint(0, 65535))

@pytest.fixture
def fake_os_sles(exclusive_lock, host):
	"""
	Trick Stacki into always seeing the OS (self.os) as SLES
	"""

	already_sles = host.file('/etc/SuSE-release').exists

	# Move the release file if needed
	if not already_sles:
		result = host.run('mv /etc/centos-release /etc/SuSE-release')
		if result.rc != 0:
			pytest.fail('unable to fake SLES OS')

	yield

	# Put things back the way they were
	if not already_sles:
		result = host.run('mv /etc/SuSE-release /etc/centos-release')
		if result.rc != 0:
			pytest.fail('unable to fake SLES OS')

@pytest.fixture
def fake_os_redhat(exclusive_lock, host):
	"""
	Trick Stacki into always seeing the OS (self.os) as Redhat (CentOS)
	"""

	already_redhat = host.file('/etc/centos-release').exists

	# Move the release file if needed
	if not already_redhat:
		result = host.run('mv /etc/SuSE-release /etc/centos-release')
		if result.rc != 0:
			pytest.fail('unable to fake Redhat OS')

	yield

	# Put things back the way they were
	if not already_redhat:
		result = host.run('mv /etc/centos-release /etc/SuSE-release')
		if result.rc != 0:
			pytest.fail('unable to fake Redhat OS')

@pytest.fixture
def rmtree(exclusive_lock, tmpdir):
	"""
	This fixture lets you call rmtree(path) in a test, which simulates
	deleting a directory and all it's files. It really moves it to
	a temperary location and restores it when the test finishes.
	"""

	restore = []
	def _inner(path):
		result = subprocess.run(['mv', path, tmpdir.join(str(len(restore)))])
		if result.returncode != 0:
			pytest.fail(f'Unable to move {path}')
		restore.append(path)

	yield _inner

	# For each directory to restore
	for ndx, path in enumerate(restore):
		# Delete any existing stuff
		if os.path.exists(path):
			shutil.rmtree(path)

		# Move back the original data
		result = subprocess.run(['mv', tmpdir.join(str(ndx)), path])
		if result.returncode != 0:
			pytest.fail(f'Unable to restory {path}')

@pytest.fixture(scope="session")
def create_pallet_isos(tmpdir_factory, test_file):
	"""
	This fixture runs at the beginning of the testing session to build
	the pallet ISOs for each roll-*.xml file found and yields their location.

	All tests will share the same ISO, so don't do anything to it. At
	the end of the session the ISO file is deleted.
	"""

	# Change to the temp directory
	temp_dir = tmpdir_factory.mktemp("pallets", False)
	with temp_dir.as_cwd():
		# Create our pallet ISOs
		for path in glob.glob(test_file('pallets/roll-*.xml')):
			subprocess.run(['stack', 'create', 'pallet', path], check=True)
			shutil.rmtree('disk1')

	yield str(temp_dir)

	# clean up temp directory
	temp_dir.remove(1, True)

@pytest.fixture(scope="session")
def create_blank_iso(tmpdir_factory):
	"""
	This fixture runs at the beginning of the testing session to build
	the blank iso file (containing nothing) and yields their location.

	All tests will share the same ISO, so don't do anything to it. At
	the end of the session the ISO file is deleted.
	"""

	temp_dir = tmpdir_factory.mktemp("blank", False)

	# Change to the temp directory
	with temp_dir.as_cwd():
		# Create our blank ISO
		subprocess.run(['genisoimage', '-o', 'blank.iso', '.'], check=True)

	yield str(temp_dir)

	# clean up temp directory
	temp_dir.remove(1, True)

@pytest.fixture
def inject_code(exclusive_lock, host):
	"""
	This returns a context manager used to inject code into the python
	runtime environment. This is currently used to inject Mock code for
	intergration tests.
	"""

	@contextmanager
	def _inner(code_file):
		result = host.run(
			f'cp "{code_file}" /opt/stack/lib/python3.7/site-packages/sitecustomize.py'
		)

		if result.rc != 0:
			pytest.fail(f'unable to inject code file "{code_file}"')

		try:
			yield
		finally:
			os.remove('/opt/stack/lib/python3.7/site-packages/sitecustomize.py')

	return _inner

@pytest.fixture
def clean_dir(tmpdir_factory):
	temp_dir = tmpdir_factory.mktemp("clean")
	old_dir = os.getcwd()
	os.chdir(temp_dir)

	yield str(temp_dir)

	os.chdir(old_dir)
	temp_dir.remove(1, True)

@pytest.fixture(scope="session")
def test_file():
	def _inner(path):
		return os.path.join("/export/test-suites/integration/files", path)

	return _inner
