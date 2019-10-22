from unittest.mock import create_autospec
import pytest
from stack.commands import DatabaseConnection
from stack.commands.list.host.firmware.mapping import Command
from stack.commands.list.host.firmware.mapping.plugin_basic import Plugin

@pytest.fixture
def basic_plugin():
	"""A fixture that returns the plugin instance for use in tests.

	This sets up the required mocks needed to construct the plugin class.
	"""
	mock_command = create_autospec(
		spec = Command,
		instance = True,
	)
	mock_command.db = create_autospec(
		spec = DatabaseConnection,
		spec_set = True,
		instance = True,
	)
	return Plugin(command = mock_command)

def test_provides(basic_plugin):
	"""Test that the provides returns the basic value."""
	assert basic_plugin.provides() == "basic"

@pytest.mark.parametrize("hosts", ("", "backend-0-0", "backend-0-1", "backend-0-0 backend-0-1"))
@pytest.mark.parametrize(
	"make, model, versions",
	(
		("", "", ""),
		("mellanox", "", ""),
		("mellanox", "m7800", ""),
		("mellanox", "m7800", "1.2.3"),
		("dell", "", ""),
		("dell", "x1052-software", ""),
		("dell", "x1052-software", "1.2.3.4"),
	),
)
@pytest.mark.parametrize("sort", ("nodes.Name", "firmware_make.name", "firmware_model.name", "firmware.version",))
def test_get_firmware_mappings(
	hosts,
	make,
	model,
	versions,
	sort,
	basic_plugin,
):
	"""Test that get_firmware_mappings filters correctly based on provided arguments."""
	# Run the function.
	basic_plugin.get_firmware_mappings(
		hosts = hosts,
		versions = versions,
		make = make,
		model = model,
		sort = sort,
	)

	query_string = basic_plugin.owner.db.select.call_args[0][0]
	query_args = basic_plugin.owner.db.select.call_args[0][1]
	# Assert we find the expected where clause and query args.
	if hosts:
		assert "nodes.Name IN %s" in query_string
		assert hosts in query_args

	if make:
		assert "firmware_make.name=%s" in query_string
		assert make in query_args

	if model:
		assert "firmware_model.name=%s" in query_string
		assert model in query_args

	if versions:
		assert "firmware.version IN %s" in query_string
		assert versions in query_args

	assert sort in query_string
