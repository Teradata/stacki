import gc
import glob
import inspect
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

import stack.firmware

@pytest.fixture
def revert_database(dump_mysql):
	# Don't need to do anything in the set up
	yield

	# Load a fresh database after each test
	with open(dump_mysql) as sql:
		subprocess.run("mysql", stdin=sql, check=True)


def _add_overlay(target):
	# Support pathlib objects.
	target = str(target)
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
	# Support pathlib objects.
	target = str(target)
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
				# or if it was specified via a usefixtures marker.
				parameters = inspect.signature(request.function).parameters
				usefixtures_marker = request.node.get_closest_marker("usefixtures")
				if request.fixturename not in parameters and (
					usefixtures_marker is None or request.fixturename not in usefixtures_marker.args
				):
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
			if attempt < 3:
				subprocess.run(["umount", f"overlay_{name}"], check=True)
			else:
				subprocess.run(["umount", "--lazy", f"overlay_{name}"], check=True)

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
def revert_export_stack_pallets(request):
	_add_overlay('/export/stack/pallets')

	yield

	_remove_overlay('/export/stack/pallets', request)

@pytest.fixture
def revert_export_stack_carts(request):
	_add_overlay('/export/stack/carts')

	yield

	_remove_overlay('/export/stack/carts', request)

@pytest.fixture
def revert_etc(request):
	_add_overlay('/etc')

	yield

	_remove_overlay('/etc', request)

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
			encoding="utf-8"
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
def revert_firmware(request):
	"""Revert the filesystem where the firmware files get laid down."""
	# Gotta make the directry first before this overlay stuff works.
	stack.firmware.BASE_PATH.mkdir(parents = True, exist_ok = True)
	_add_overlay(stack.firmware.BASE_PATH)

	yield

	_remove_overlay(stack.firmware.BASE_PATH, request)
