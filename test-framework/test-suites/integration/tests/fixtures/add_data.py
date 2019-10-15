import json
import subprocess

import pytest


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
def add_host_with_net(host):
	host.run("stack add network test pxe=true address=192.168.0.0 mask=255.255.255.0")
	host.run("stack add host interface a:frontend interface=eth2 network=test ip=192.168.0.2")
	host.run("stack add host backend-0-0 appliance=backend rack=0 rank=0")
	host.run("stack add host interface backend-0-0 interface=eth0 network=test ip=192.168.0.3")

@pytest.fixture(params = (True, False))
def stack_load(request, host):
	if request.param:
		def _load_using_exec(dump_file, **kwargs):
			kwargs_string = " ".join(f"{key}={value}" for key, value in kwargs.items())
			return host.run(f"stack load {dump_file} exec=True {kwargs_string}")

		return _load_using_exec

	def _load_using_bash(dump_file, **kwargs):
		kwargs_string = " ".join(f"{key}={value}" for key, value in kwargs.items() if key != "exec")
		return host.run(f"stack load {dump_file} {kwargs_string} | bash -x")

	return _load_using_bash
