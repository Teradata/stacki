from contextlib import contextmanager
import gc
import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler
import inspect
import json
import multiprocessing
import os
import random
import shutil
import signal
import subprocess
import tempfile
import time
import warnings

from django.core.servers import basehttp
from django.core.wsgi import get_wsgi_application
import pytest
from redis import StrictRedis


def pytest_addoption(parser):
	parser.addoption(
		"--audit", action="store_true", help="audit filesystem changes"
	)

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

	# Dump the initial Stacki DB into an SQL file, to restore from after each test
	subprocess.run([
		"mysqldump", "--opt", "--add-drop-database", "--databases", "cluster", "shadow"
	], stdout=file_obj, check=True)

	# Close the file
	file_obj.close()

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

	# Done with the set up, yield our SQL file path
	yield file_path

	# Remove the SQL file
	os.remove(file_path)

	# Drop our process specific dbs
	subprocess.run(['mysql', '-e', f'DROP DATABASE `cluster{worker_id}`'], check=True)
	subprocess.run(['mysql', '-e', f'DROP DATABASE `shadow{worker_id}`'], check=True)

@pytest.fixture
def revert_database(dump_mysql, redis):
	# Don't need to do anything in the set up
	yield

	# Load a fresh database after each test
	with redis.lock("pytest_revert_database"):
		with open(dump_mysql) as sql:
			subprocess.run("mysql", stdin=sql, check=True)

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

def _add_overlay(target):
	name = target[1:].replace("/", "_")

	# Make an overlay directories
	overlay_dirs = {
		"lowerdir": target,
		"upperdir": f"/overlay/{name}/upper",
		"workdir": f"/overlay/{name}/work"
	}

	if os.path.exists(f"/overlay/{name}"):
		shutil.rmtree(f"/overlay/{name}")

	os.makedirs(overlay_dirs["upperdir"])
	os.makedirs(overlay_dirs["workdir"])

	# Mount the overlays
	subprocess.run([
		"mount",
		"-t", "overlay",
		f"overlay_{name}",
		"-o", ",".join(f"{k}={v}" for k, v in overlay_dirs.items()),
		target
	], check=True)

def _remove_overlay(target, request):
	name = target[1:].replace("/", "_")

	# Log any file changes, if requested
	if request.config.getoption('--audit'):
		# Run the garbase collector, just in case it releases
		# some opened file handles
		gc.collect()

		# Do a sync also, just in case
		subprocess.run(["sync"], check=True)

		with open(f'/export/reports/revert_{name}.log', 'a') as f:
			cwd = os.getcwd()
			os.chdir(f'/overlay/{name}/upper')

			mods = glob.glob('**/*', recursive=True)
			if mods:
				# Write out what was modified
				f.write('TEST: {}\n'.format(request.node.nodeid))
				f.write('{}\n\n'.format('\n'.join(sorted(mods))))

				# Check if the fixture is part of the function parameters
				parameters = inspect.signature(request.function).parameters
				if request.fixturename not in parameters:
					request.node.warn(pytest.PytestWarning(
						f"'{request.fixturename}' fixture is missing"
					))

			os.chdir(cwd)

	# Try three times to unmount the overlay
	for attempt in range(1, 4):
		try:
			# Run the garbase collector, just in case it releases
			# some opened file handles
			gc.collect()

			# Do a sync also, just in case
			subprocess.run(["sync"], check=True)

			# Then try to unmount the overlay
			subprocess.run(["umount", f"overlay_{name}"], check=True)

			# It succeeded
			break
		except subprocess.CalledProcessError:
			if attempt < 3:
				# Sleep for a few seconds to give the open file
				# handles a chance to clean themselves up
				time.sleep(3)
	else:
		# We couldn't unmount the overlay
		pytest.fail(f"Unable to unmount overlay_{name}")

	# Clean up the overlay directories
	shutil.rmtree(f"/overlay/{name}")

@pytest.fixture
def revert_export_stack_pallets(exclusive_lock, request):
	_add_overlay('/export/stack/pallets')

	yield

	_remove_overlay('/export/stack/pallets', request)

@pytest.fixture
def revert_export_stack_carts(exclusive_lock, request):
	_add_overlay('/export/stack/carts')

	yield

	_remove_overlay('/export/stack/carts', request)

@pytest.fixture
def revert_etc(exclusive_lock, request):
	_add_overlay('/etc')

	yield

	_remove_overlay('/etc', request)

@pytest.fixture
def revert_discovery(exclusive_lock):
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
def revert_routing_table(exclusive_lock):
	# Get a snapshot of the existing routes
	result = subprocess.run(
		["ip", "route", "list"],
		stdout=subprocess.PIPE,
		encoding="utf-8",
		check=True
	)
	old_routes = { line.strip() for line in result.stdout.split('\n') if line }

	yield

	# Get a new view of the routing table
	result = subprocess.run(
		["ip", "route", "list"],
		stdout=subprocess.PIPE,
		encoding="utf-8",
		check=True
	)
	new_routes = { line.strip() for line in result.stdout.split('\n') if line }

	# Remove any new routes
	for route in new_routes:
		if route not in old_routes:
			result = subprocess.run(f"ip route del {route}", shell=True)

	# Add in any missing old routes
	for route in old_routes:
		if route not in new_routes:
			result = subprocess.run(f"ip route add {route}", shell=True)

@pytest.fixture
def add_host():
	def _inner(hostname, rack, rank, appliance):
		cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance={appliance}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to add a dummy host')

	# First use of the fixture adds backend-0-0
	_inner('backend-0-0', '0', '0', 'backend')

	# Then return the inner function, so we can call it inside the test
	# to get more hosts added
	return _inner

@pytest.fixture
def add_host_with_interface():
	def _inner(hostname, rack, rank, appliance, interface):
		cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance={appliance}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to add a dummy host')

		cmd = f'stack add host interface {hostname} interface={interface}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to add a dummy interface')

	_inner('backend-0-0', '0', '1', 'backend', 'eth0')

	return _inner

@pytest.fixture
def add_ib_switch():
	def _inner(hostname, rack, rank, appliance, make, model, sw_type):
		cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance={appliance}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to add a dummy host')

		cmd = f'stack set host attr {hostname} attr=component.make value={make}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to set make')

		cmd = f'stack set host attr {hostname} attr=component.model value={model}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to set model')

		cmd = f'stack set host attr {hostname} attr=switch_type value={sw_type}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to set switch type')

	_inner('switch-0-0', '0', '0', 'switch', 'Mellanox', 'm7800', 'infiniband')

	return _inner

@pytest.fixture
def add_ib_switch_partition():
	def _inner(switch_name, partition_name, options):
		cmd = f'stack add switch partition {switch_name} name={partition_name} '
		if options is not None:
			cmd += f'options={options}'

		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to add a dummy switch partition')

	_inner('switch-0-0', 'Default', '')

	return _inner

@pytest.fixture
def add_switch():
	def _inner(hostname, rack, rank, appliance, make, model):
		cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance={appliance}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to add a dummy host')

		cmd = f'stack set host attr {hostname} attr=component.make value={make}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to set make')

		cmd = f'stack set host attr {hostname} attr=component.model value={model}'
		result = subprocess.run(cmd.split())
		if result.returncode != 0:
			pytest.fail('unable to set model')

	_inner('switch-0-0', '0', '0', 'switch', 'fake', 'unrl')

	return _inner

@pytest.fixture
def add_appliance(host):
	def _inner(name):
		result = host.run(f'stack add appliance {name}')
		if result.rc != 0:
			pytest.fail(f'unable to add dummy appliance "{name}"')

	# First use of the fixture adds appliance "test"
	_inner('test')

	# Then return the inner function, so we can call it inside the test
	# to get more appliances added
	return _inner

@pytest.fixture
def add_box(host):
	def _inner(name):
		result = host.run(f'stack add box {name}')
		if result.rc != 0:
			pytest.fail(f'unable to add dummy box "{name}"')

	# First use of the fixture adds box "test"
	_inner('test')

	# Then return the inner function, so we can call it inside the test
	# to get more boxes added
	return _inner

@pytest.fixture
def add_cart(host):
	def _inner(name):
		result = host.run(f'stack add cart {name}')
		if result.rc != 0:
			pytest.fail(f'unable to add dummy cart "{name}"')

	# First use of the fixture adds cart "test"
	_inner('test')

	# Then return the inner function, so we can call it inside the test
	# to get more carts added
	return _inner

@pytest.fixture
def add_environment(host):
	def _inner(name):
		result = host.run(f'stack add environment {name}')
		if result.rc != 0:
			pytest.fail(f'unable to add dummy environment "{name}"')

	# First use of the fixture adds environment "test"
	_inner('test')

	# Then return the inner function, so we can call it inside the test
	# to get more environments added
	return _inner

@pytest.fixture
def add_group(host):
	def _inner(name):
		result = host.run(f'stack add group {name}')
		if result.rc != 0:
			pytest.fail(f'unable to add dummy group "{name}"')

	# First use of the fixture adds group "test"
	_inner('test')

	# Then return the inner function, so we can call it inside the test
	# to get more groups added

	return _inner


@pytest.fixture
def add_network(host):
	def _inner(name, address):
		result = host.run(
			f'stack add network {name} address={address} mask=255.255.255.0'
		)
		if result.rc != 0:
			pytest.fail(f'unable to add dummy network "{name}"')

	# First use of the fixture adds network "test"
	_inner('test', '192.168.0.0')

	# Then return the inner function, so we can call it inside the test
	# to get more networks added

	return _inner

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

@pytest.fixture
def run_django_server(exclusive_lock):
	# Run a Django server in a process
	def runner():
		try:
			os.environ['DJANGO_SETTINGS_MODULE'] = 'stack.restapi.settings'
			basehttp.run('127.0.0.1', 8000, get_wsgi_application())
		except KeyboardInterrupt:
			# The signal to exit
			pass

	process = multiprocessing.Process(target=runner)
	process.daemon = True
	process.start()

	# Give the server a few seconds to get ready
	time.sleep(2)

	yield

	# Tell the server it is time to clean up
	os.kill(process.pid, signal.SIGINT)
	process.join()

@pytest.fixture
def run_file_server(exclusive_lock):
	# Run an HTTP server in a process
	def runner():
		try:
			# Change to our test-files directory
			os.chdir('/export/test-files')

			# Serve them up
			with HTTPServer(
				('127.0.0.1', 8000),
				SimpleHTTPRequestHandler
			) as httpd:
				httpd.serve_forever()
		except KeyboardInterrupt:
			# The signal to exit
			pass

	process = multiprocessing.Process(target=runner)
	process.daemon = True
	process.start()

	# Give us a second to get going
	time.sleep(1)

	yield

	# Tell the server it is time to clean up
	os.kill(process.pid, signal.SIGINT)
	process.join()

@pytest.fixture
def run_pallet_isos_server(exclusive_lock, create_pallet_isos):
	# Run an HTTP server in a process
	def runner():
		try:
			# Change to our test-files directory
			os.chdir(create_pallet_isos)

			# Serve them up
			with HTTPServer(
				('127.0.0.1', 8000),
				SimpleHTTPRequestHandler
			) as httpd:
				httpd.serve_forever()
		except KeyboardInterrupt:
			# The signal to exit
			pass

	process = multiprocessing.Process(target=runner)
	process.daemon = True
	process.start()

	# Give us a second to get going
	time.sleep(1)

	yield

	# Tell the server it is time to clean up
	os.kill(process.pid, signal.SIGINT)
	process.join()

@pytest.fixture(scope="session")
def host_os():
	if os.path.exists('/etc/SuSE-release'):
		return 'sles'

	return 'redhat'

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

@pytest.fixture
def invalid_host():
	return 'invalid-{:04x}'.format(random.randint(0, 65535))

@pytest.fixture(scope="session")
def create_pallet_isos(tmpdir_factory):
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
		for path in glob.glob('/export/test-files/pallets/roll-*.xml'):
			subprocess.run(['stack', 'create', 'pallet', path], check=True)
			shutil.rmtree('disk1')

	yield str(temp_dir)

	# clean up temp directory
	temp_dir.remove(1, True)

@pytest.fixture(scope="session")
def create_blank_iso(tmpdir_factory):
	"""
	This fixture runs at the beginning of the testing session to build
	the blank iso file (containing nothing) and copies it to the
	/export/test-files/pallets/ folder.

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
			f'cp "{code_file}" /opt/stack/lib/python3.6/site-packages/sitecustomize.py'
		)

		if result.rc != 0:
			pytest.fail(f'unable to inject code file "{code_file}"')

		try:
			yield
		finally:
			os.remove('/opt/stack/lib/python3.6/site-packages/sitecustomize.py')

	return _inner

@pytest.fixture
def clean_dir(tmpdir_factory):
	temp_dir = tmpdir_factory.mktemp("clean")
	old_dir = os.getcwd()
	os.chdir(temp_dir)

	yield str(temp_dir)

	os.chdir(old_dir)
	temp_dir.remove(1, True)
