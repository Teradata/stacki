import json
import pytest

@pytest.mark.parametrize(
	"hosts, expected_results",
	(
		(
			"",
			[
				{"host": "backend-0-0", "version": "1.2.3", "make": "mellanox", "model": "m7800"},
				{"host": "backend-0-1", "version": "1.2.3.4", "make": "dell", "model": "x1052-software"},
			],
		),
		("backend-0-0", [{"host": "backend-0-0", "version": "1.2.3", "make": "mellanox", "model": "m7800"}]),
		("backend-0-1", [{"host": "backend-0-1", "version": "1.2.3.4", "make": "dell", "model": "x1052-software"}]),
	),
)
def test_list_host_firmware_mapping_host_filter(
	host,
	add_host_with_net,
	fake_local_firmware_file,
	revert_firmware,
	hosts,
	expected_results,
):
	"""Test that list host firmware mapping filters correctly based on provided arguments."""
	# Add a backend-0-1
	add_host_with_net(
		hostname = "backend-0-1",
		rack = 0,
		rank = 1,
		appliance = "backend",
		interface = "eth0",
		ip = "192.168.1.1",
		network = "fake_net",
		address = "192.168.1.0",
		pxe = True,
	)
	# Add a piece of mellanox firmware to backend-0-0.
	result = host.run(f"stack add firmware 1.2.3 make=mellanox model=m7800 source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	# Add a piece of dell firmware to backend-0-1
	result = host.run(f"stack add firmware 1.2.3.4 make=dell model=x1052-software source={fake_local_firmware_file} hosts=backend-0-1")
	assert result.rc == 0

	# List the firmware mappings
	result = host.run(f"stack list host firmware mapping {hosts} output-format=json")
	assert result.rc == 0
	assert expected_results == json.loads(result.stdout)

@pytest.mark.parametrize(
	"make, model, versions, expected_results",
	(
		(
			"",
			"",
			"",
			[
				{"host": "backend-0-0", "version": "1.2.3", "make": "mellanox", "model": "m7800"},
				{"host": "backend-0-1", "version": "1.2.3.4", "make": "dell", "model": "x1052-software"},
			],
		),
		("mellanox", "", "", [{"host": "backend-0-0", "version": "1.2.3", "make": "mellanox", "model": "m7800"}]),
		("mellanox", "m7800", "", [{"host": "backend-0-0", "version": "1.2.3", "make": "mellanox", "model": "m7800"}]),
		("mellanox", "m7800", "1.2.3", [{"host": "backend-0-0", "version": "1.2.3", "make": "mellanox", "model": "m7800"}]),
		("dell", "", "", [{"host": "backend-0-1", "version": "1.2.3.4", "make": "dell", "model": "x1052-software"}]),
		("dell", "x1052-software", "", [{"host": "backend-0-1", "version": "1.2.3.4", "make": "dell", "model": "x1052-software"}]),
		("dell", "x1052-software", "1.2.3.4", [{"host": "backend-0-1", "version": "1.2.3.4", "make": "dell", "model": "x1052-software"}]),
	),
)
def test_list_host_firmware_mapping_non_host_filter(
	host,
	add_host_with_net,
	fake_local_firmware_file,
	revert_firmware,
	make,
	model,
	versions,
	expected_results,
):
	"""Test that list host firmware mapping filters correctly based on provided arguments."""
	# Add a backend-0-1
	add_host_with_net(
		hostname = "backend-0-1",
		rack = 0,
		rank = 1,
		appliance = "backend",
		interface = "eth0",
		ip = "192.168.1.1",
		network = "fake_net",
		address = "192.168.1.0",
		pxe = True,
	)
	# Add a piece of mellanox firmware to backend-0-0.
	result = host.run(f"stack add firmware 1.2.3 make=mellanox model=m7800 source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	# Add a piece of dell firmware to backend-0-1
	result = host.run(f"stack add firmware 1.2.3.4 make=dell model=x1052-software source={fake_local_firmware_file} hosts=backend-0-1")
	assert result.rc == 0

	# List the firmware mappings
	result = host.run(
		f"stack list host firmware mapping {f'make={make}' if make else ''} {f'model={model}' if model else ''} "
		f"{f'versions={versions}' if versions else ''} output-format=json"
	)
	assert result.rc == 0
	assert expected_results == json.loads(result.stdout)
