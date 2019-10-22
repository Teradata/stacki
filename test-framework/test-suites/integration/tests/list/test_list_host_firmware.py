import json
import pytest

@pytest.mark.parametrize(
	"hosts, expected_results",
	(
		(
			"",
			[
				{"host": "backend-0-0", "make": "mellanox", "model": "m7800", "desired_firmware_version": "1.2.3", "current_firmware_version": "0.0.0"},
				{"host": "backend-0-1", "make": "dell", "model": "x1052-software", "desired_firmware_version": "1.2.3.4", "current_firmware_version": "0.0.0.0"},
				{"host": "frontend-0-0", "make": None, "model": None, "desired_firmware_version": None, "current_firmware_version": None},
			],
		),
		(
			"backend-0-0",
			[{"host": "backend-0-0", "make": "mellanox", "model": "m7800", "desired_firmware_version": "1.2.3", "current_firmware_version": "0.0.0"}],
		),
		(
			"backend-0-1",
			[{"host": "backend-0-1", "make": "dell", "model": "x1052-software", "desired_firmware_version": "1.2.3.4", "current_firmware_version": "0.0.0.0"}],
		),
	),
)
def test_list_host_firmware(
	host,
	add_host_with_net,
	fake_local_firmware_file,
	revert_firmware,
	inject_code,
	test_file,
	hosts,
	expected_results,
):
	"""Test that list host firmware filters correctly based on provided arguments."""
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

	# Now list the firmware. We need to mock out the running of plugins so it doesn't
	# actually try to talk to hardware that doesn't exist.
	with inject_code(test_file("list/mock_list_firmware_run_plugins.py")):
		result = host.run(f"stack list host firmware {hosts} output-format=json")
		assert result.rc == 0
		assert json.loads(result.stdout) == expected_results
