import pytest
import os
from pathlib import Path
from stack.util import _exec
from tempfile import TemporaryDirectory
from contextlib import ExitStack

@pytest.fixture
def add_vm():

	# Need to add a VM as a host first
	add_host = f'stack add host vm-backend-0-3 appliance=backend rack=0 rank=3'
	host_result = _exec(add_host, shlexsplit = True)

	if host_result.returncode != 0:
		pytest.fail(f'Unable to add host vm-backend-0-3:\n{host_result.stderr}')

	add_vm = (
		f'stack add vm vm-backend-0-3 '
		f'hypervisor=hypervisor-0-1 cpu=1 memory=2048 '
		f'storage_pool=/export/pools/stacki disks=100'
	)
	vm_result = _exec(add_vm, shlexsplit = True)
	if vm_result.returncode != 0:
		pytest.fail(f'Unable to add VM vm-backend-0-3:\n{vm_result.stderr}')

@pytest.fixture
def add_vm_multiple():
	def _inner(hostname, hypervisor, cpu, memory, storloc, disks, ip, mac, rank):

		# Need to add a VM as a host first
		add_host = f'stack add host {hostname} appliance=backend rack=0 rank=3'
		host_result = _exec(add_host, shlexsplit = True)
		if host_result.returncode != 0:
			pytest.fail(f'Unable to add host {hostname}:\n{host_result.stderr}')

		# Add an interface
		add_interface = (
			f'stack add host interface {hostname} '
			f'default=y interface=eth0 ip={ip} mac={mac} network=private'
		)
		interface_result = _exec(add_interface, shlexsplit=True)
		if interface_result.returncode != 0:
			pytest.fail(f'Unable to add interface to {hostname}')

		# Add it as a virtual machine
		add_vm = (
			f'stack add vm {hostname} '
			f'hypervisor={hypervisor} cpu={cpu} memory={memory} '
			f'storage_pool={storloc} disks={disks}'
		)
		vm_result = _exec(add_vm, shlexsplit = True)
		if vm_result.returncode != 0:
			pytest.fail(f'Unable to add VM {hostname}:\n{vm_result.stderr}')

	_inner(
		'vm-backend-0-3',
		'hypervisor-0-1',
		'1',
		'2048',
		'/export/pools/stacki',
		'100',
		'192.168.0.2',
		'52:54:00:4a:7d:91',
		'3'
	)
	_inner(
		'vm-backend-0-4',
		'hypervisor-0-1',
		'2',
		'2048',
		'/export/pools/stacki',
		'200,100',
		'192.168.0.3',
		'52:54:00:7a:f0:1f',
		'4'
	)
	_inner(
		'vm-backend-0-5',
		'hypervisor-0-2',
		'3', '3072',
		'/export/pools/stacki',
		'200,100',
		'192.168.0.4',
		'52:54:00:bf:9f:e8',
		'5'
	)
	_inner(
		'vm-backend-0-6',
		'hypervisor-0-2',
		'4',
		'4096',
		'/export/pools/stacki',
		'200,/dev/sdc',
		'192.168.0.5',
		'52:54:00:c4:c9:b9',
		'6'
	)

@pytest.fixture
def add_hypervisor():
	def _inner(hostname, rack, rank, hypervisor, ip):

		# Add the correct appliance
		# and ignore if the appliance
		# was already created
		app_cmd = f'stack add appliance hypervisor'
		result = _exec(app_cmd, shlexsplit=True)
		if result.returncode != 0 and 'appliance "hypervisor" already exists' not in result.stderr:
			pytest.fail(f'Unable to add hypervisor appliance {result.stdout} {result.stderr}')
		app_cmd2 = f'stack add appliance attr hypervisor attr=hypervisor value=True'
		result = _exec(app_cmd2, shlexsplit=True)

		host_cmd = f'stack add host {hostname} rack={rack} rank={rank} appliance=hypervisor'

		# Add the host
		result = _exec(host_cmd, shlexsplit=True)
		if result.returncode != 0:
			pytest.fail(f'Unable to add hypervisor {hostname} {result.stdout} {result.stderr}')

		# Add an interface
		add_interface = (
			f'stack add host interface {hostname} '
			f'default=y interface=eth0 ip={ip} network=private'
		)
		interface_result = _exec(add_interface, shlexsplit=True)
		if interface_result.returncode != 0:
			pytest.fail(f'Unable to add interface to {hostname}: \n{interface_result.stderr}')

	_inner('hypervisor-0-1', '0', '1', 'hypervisor', '192.168.0.6')
	_inner('hypervisor-0-2', '0', '2', 'hypervisor', '192.168.0.7')

	return _inner

@pytest.fixture
def create_image_files():

	# Given a temp folder create blank disk images
	# to replicate vm images being adding them to Stacki
	# Returns a list of Path objects to the image files
	def _inner(folder):
		disks = {}
		cur_dir = Path.cwd()

		with ExitStack() as cleanup:
			os.chdir(folder.name)
			cleanup.callback(os.chdir, cur_dir)

			# Create qcow2 and raw image files
			_exec(f'qemu-img create -f raw image1.raw 100M', shlexsplit=True)
			disks['image1.raw'] = Path(f'{folder.name}/image1.raw')

			_exec(f'qemu-img create -f qcow2 image2.qcow2 100M', shlexsplit=True)
			disks[f'image2.qcow2'] = Path(f'{folder.name}/image2.qcow2')

			return disks
	return _inner

@pytest.fixture
def create_invalid_image():

	# Return the location of an "invalid"
	# disk image file for testing bad input
	# when a real file/path is needed
	def _inner(folder):
		cur_dir = Path.cwd()
		with ExitStack() as cleanup:
			os.chdir(folder.name)
			cleanup.callback(os.chdir, cur_dir)
			_exec(f'touch image3.txt', shlexsplit=True)
			return Path(f'{folder.name}/image3.txt')
	return _inner

@pytest.fixture
def add_vm_storage():

	# Add a	all types of VM storage
	# to a given host
	def _inner(images, host):
		disks = [str(path) for disk, path in images.items()]

		# Add the new disks
		cmd =(
			f'stack add vm storage {host} '
			f'storage_pool=/export/pools/stacki disks={",".join(disks)},/dev/sdb'
		)
		add_stor = _exec(cmd, shlexsplit=True)
		assert add_stor.returncode == 0
	return _inner
