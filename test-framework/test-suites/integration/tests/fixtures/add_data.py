import json
import subprocess
import ipaddress
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

	_inner('backend-0-0', '0', '0', 'backend', 'eth0')

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
	"""Adds a network to the stacki db. For historical reasons the first test network this creates is pxe=False."""
	def _inner(name, address, pxe = False):
		result = host.run(
			f'stack add network {name} address={address} mask=255.255.255.0 pxe={pxe}'
		)
		if result.rc != 0:
			pytest.fail(f'unable to add dummy network "{name}"')

	# First use of the fixture adds network "test"
	_inner('test', '192.168.0.0')

	# Then return the inner function, so we can call it inside the test
	# to get more networks added

	return _inner

@pytest.fixture
def add_host_with_net(host, add_host_with_interface, add_network):
	"""Adds a host with a network. The first network this adds defaults to pxe=True."""
	def _inner(hostname, rack, rank, appliance, interface, ip, network, address, pxe):
		# Add the host with an interface.
		add_host_with_interface(hostname = hostname, rack = rack, rank = rank, appliance = appliance, interface = interface)

		# Add the network.
		add_network(name = network, address = address, pxe = pxe)

		# Associate it to the interface.
		result = host.run(f"stack set host interface network {hostname} network={network} interface={interface}")
		assert result.rc == 0

		# Set the interface IP
		result = host.run(f"stack set host interface ip {hostname} ip={ip} network={network}")
		assert result.rc == 0

		# Add it to the frontend, because a lot of things in stacki expect backends to share networks with
		# frontends.
		result = host.run("stack list host interface a:frontend output-format=json")
		assert result.rc == 0
		# Try to figure out if the frontend has an interface on this network already.
		interface_on_network = False
		for frontend_interface in json.loads(result.stdout):
			if frontend_interface["network"] == network:
				interface_on_network = True
				break

		if interface_on_network:
			return

		# Need to add an interface to the frontend on this network. Make sure we choose the next latest
		# interface name so we don't clash with other interface names.
		latest_interface = max(frontend_interface["interface"] for frontend_interface in json.loads(result.stdout))
		# This should be a string, so we tokenize it into characters
		new_interface = list(latest_interface)
		new_interface[-1] = str(int(new_interface[-1]) + 1)
		new_interface = "".join(new_interface)
		result = host.run(f"stack add host interface a:frontend interface={new_interface} network={network} ip={ipaddress.ip_address(ip) + 1}")
		assert result.rc == 0

	# First use of the add_host_with_interface fixture adds backend-0-0 with interface eth0.
	# The first use of add_network adds a network called test, but that's not PXE so we don't want to use it.
	# So the first call of this fixture needs to remove the test network, recreate it as a PXE network, and
	# associate the network with the host's interface.
	result = host.run(f"stack remove network test")
	assert result.rc == 0
	add_network(name = "test", address = "192.168.0.0", pxe = True)
	result = host.run(f"stack set host interface network backend-0-0 network=test interface=eth0 ip=192.168.0.3")
	assert result.rc == 0

	# Add a frontend interface on the network.
	result = host.run(f"stack add host interface a:frontend interface=eth2 network=test ip=192.168.0.2")
	assert result.rc == 0

	return _inner

@pytest.fixture(
	params = (
		("", "exec=True"),
		("", "| bash -x"),
		("document=", "exec=True"),
		("document=", "| bash -x"),
	),
	ids = ("stack_load_exec", "stack_load_bash", "stack_load_document_exec", "stack_load_document_bash"),
)
def stack_load(request, host):
	"""This fixture is used to run `stack load` on the host during integration tests.

	There are 4 essentially equivalent ways of loading and running a dump.json. Using
	this test fixture ensures that all 4 are tested. I.E:

	stack load dump_file exec=True
	stack load document=dump_file exec=True
	stack load dump_file | bash -x
	stack load document=dump_file | bash -x
	"""
	param_string, exec_string = request.param
	def _load(dump_file, **kwargs):
		if "exec" in kwargs:
			raise ValueError("Cannot pass exec param to this fixture. It handles it for you.")

		if "document" in kwargs:
			raise ValueError("Cannot pass document param to this fixture. It handles it for you.")

		kwargs_string = " ".join(f"{key}={value}" for key, value in kwargs.items())
		return host.run(f"stack load {param_string}{dump_file} {exec_string} {kwargs_string}")

	return _load

@pytest.fixture
def fake_local_firmware_file(tmp_path_factory):
	"""Creates a fake local firmware file and returns a pathlib.Path object that points to it."""
	# Add a fake piece of firmware.
	fake_firmware_file = tmp_path_factory.mktemp("fake_firmware") / "foo.img"
	fake_firmware_file.write_text("foofakefirmware")
	return fake_firmware_file
