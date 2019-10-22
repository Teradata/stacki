from collections import namedtuple
from unittest.mock import patch
import stack.commands.sync.host.firmware
import stack.commands.list.host.firmware.imp_mellanox
import stack.commands.list.host.firmware.imp_dell_x1052

# Make the mellanox implementation for list host firmware return a low version
# number that will be a candidate for upgrading.
mock_mellanox_list_firmware = patch.object(
	target = stack.commands.list.host.firmware.imp_mellanox.Implementation,
	attribute = "list_firmware",
	autospec = True,
).start()
mock_mellanox_list_firmware.return_value = "0.0.0"

# Make the dell implementation for list host firmware return a low version
# number that will be a candidate for upgrading.
mock_dell_list_firmware = patch.object(
	target = stack.commands.list.host.firmware.imp_dell_x1052.Implementation,
	attribute = "list_firmware",
	autospec = True,
).start()
mock_dell_list_firmware.return_value = namedtuple("Versions", ("software", "boot", "hardware"))(
	software = "0.0.0.0",
	boot = "0.0.0.0",
	hardware = "0.0.0.0",
)

# Mock runPlugins calls
patch.object(
	target = stack.commands.sync.host.firmware.Command,
	attribute = "runPlugins",
	autospec = True,
).start()
