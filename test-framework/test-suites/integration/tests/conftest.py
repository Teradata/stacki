from contextlib import contextmanager
import gc
import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler
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


@pytest.fixture(scope="session")
def dump_mysql():
	# Create a temp file and open it for the subprocess command
	file_fd, file_path = tempfile.mkstemp(suffix=".sql")
	file_obj = os.fdopen(file_fd, mode="w")

	# Dump the initial Stacki DB into an SQL file, to restore from
	# after each test
	subprocess.run([
		"mysqldump", "--opt", "--add-drop-database", "--databases", "cluster", "shadow"
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
		subprocess.run("mysql", stdin=sql, check=True)

@pytest.fixture
def revert_filesystem():
	# The paths to capture and revert changes to
	paths = (
		"/etc",
		"/export/stack",
		"/tftpboot"
	)

	def clean_up():
		# Unmount any existing overlay directories
		with open("/proc/mounts", "r") as mounts:
			# Create a tuple of lines because /proc/mounts will change
			# as we unmount things
			for mount in tuple(mounts):
				if mount.startswith("overlay_"):
					# Try three times to unmount the overlay
					for attempt in range(1, 4):
						try:
							subprocess.run(
								["umount", mount.split()[0]],
								check=True
							)

							# It succeeded
							break
						except subprocess.CalledProcessError:
							# Let's run sync to see if it helps
							subprocess.run(["sync"])
							
							# Run the garbase collector, just in case it releases
							# some opened file handles
							gc.collect()

							if attempt < 3:
								# Sleep for a few seconds to give the open file
								# handles a chance to clean themselves up
								time.sleep(3)
					else:
						# Let's dump out any suspects.
						result = subprocess.run(
							["lsof", "-x", "+D", mount.split()[1]],
							stdout=subprocess.PIPE,
							encoding='utf-8'
						)

						warnings.warn('Unable to unmount {} mounted on {}\n\n{}'.format(
							mount.split()[0], 
							mount.split()[1],
							result.stdout
						))

						# We couldn't unmount the overlay, abort the tests
						pytest.exit("Couldn't unmount overlay on {}".format(mount.split()[1]))

		# Make sure the overlay root is clean
		if os.path.exists("/overlay"):
			shutil.rmtree("/overlay")

	# Make sure we are clean
	clean_up()

	# Now set up the overlays
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
	
	yield

	# Clean up after the test
	clean_up()

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
def revert_routing_table():
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
			pytest.fail(f'unable to add cart box "{name}"')

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
def run_django_server():
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
def run_file_server():
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
def host_os(host):
	if host.file('/etc/SuSE-release').exists:
		return 'sles'

	return 'redhat'

@pytest.fixture
def fake_os_sles(host):
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
def fake_os_redhat(host):
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
def rmtree(tmpdir):
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
	the pallet ISOs for each roll-*.xml file found and copies them to
	the /export/test-files/pallets/ folder.

	All tests will share the same ISO, so don't do anything to it. At
	the end of the session the ISO file is deleted.
	"""

	clean_up = []

	# Change to the temp directory
	temp_dir = tmpdir_factory.mktemp("pallets", False)
	with temp_dir.as_cwd():
		# Create our pallet ISOs
		for path in glob.glob('/export/test-files/pallets/roll-*.xml'):
			subprocess.run(['stack', 'create', 'pallet', path], check=True)
			shutil.rmtree('disk1')

		# Move our new ISOs where the tests expect them
		for path in glob.glob('*.iso'):
			shutil.move(path, '/export/test-files/pallets/')
			clean_up.append(path)
	yield

	# Clean up the ISO files
	for filename in clean_up:
		os.remove(os.path.join('/export/test-files/pallets/', filename))

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

		# Move our new ISO where the tests expect it
		shutil.move(
			temp_dir.join('blank.iso'),
			'/export/test-files/pallets/blank.iso'
		)

	yield

	# Clean up the ISO file
	os.remove('/export/test-files/pallets/blank.iso')

@pytest.fixture
def inject_code(host):
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
