from unittest.mock import create_autospec, patch, ANY, call
import pytest
from contextlib import ExitStack
from stack.commands import DatabaseConnection
from stack.commands.add.host.firmware.mapping import Command
from stack.commands.add.host.firmware.mapping.plugin_basic import Plugin
from stack.exception import CommandError

class TestAddHostFirmwareMappingBasicPlugin:
	"""A test case for the add host firmware mapping basic plugin."""

	@pytest.fixture
	def basic_plugin(self):
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

	def test_provides(self, basic_plugin):
		"""Ensure the plugin returns the correct provides information."""
		assert basic_plugin.provides() == "basic"

	def test_ensure_unique_mappings(self, basic_plugin):
		"""Test that ensure_unique_mappings queries the db as expected."""
		mock_hosts = ["foo", "bar"]
		mock_make = "baz"
		mock_model = "bag"
		mock_version = "bam"
		basic_plugin.owner.db.select.return_value = []

		basic_plugin.ensure_unique_mappings(
			hosts = mock_hosts,
			version = mock_version,
			make = mock_make,
			model = mock_model,
		)

		basic_plugin.owner.db.select.assert_called_once_with(
			ANY,
			(mock_hosts, mock_make, mock_model, mock_version),
		)

	def test_ensure_unique_mappings_error(self, basic_plugin):
		"""Test that ensure_unique_mappings fails if matching mappings are found."""
		mock_hosts = ["foo", "bar"]
		mock_make = "baz"
		mock_model = "bag"
		mock_version = "bam"
		basic_plugin.owner.db.select.return_value = [[mock_hosts[0], mock_make, mock_model, mock_version]]

		with pytest.raises(CommandError):
			basic_plugin.ensure_unique_mappings(
				hosts = mock_hosts,
				version = mock_version,
				make = mock_make,
				model = mock_model,
			)

	@patch.object(target = Plugin, attribute = "ensure_unique_mappings", autospec = True)
	@patch(target = "stack.commands.add.host.firmware.mapping.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.host.firmware.mapping.plugin_basic.unique_everseen", autospec = True)
	def test_run(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_ensure_unique_mappings,
		basic_plugin,
	):
		"""Test that run works as expected when the params and args are valid."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"version": "bam!", "make": "fizz", "model": "buzz"}
		expected_hosts = tuple(mock_args)
		mock_lowered.return_value = mock_params.values()
		mock_unique_everseen.return_value = mock_args
		basic_plugin.owner.getHosts.return_value = expected_hosts
		basic_plugin.owner.db.select.return_value = [["1"]]

		basic_plugin.run(args = (mock_params, mock_args))

		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.getHosts.assert_called_once_with(args = expected_hosts)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("version", ""),
				("make", ""),
				("model", ""),
			],
			params = mock_params,
		)
		basic_plugin.owner.ensure_firmware_exists.assert_called_once_with(
			make = mock_params["make"],
			model = mock_params["model"],
			version = mock_params["version"],
		)
		mock_ensure_unique_mappings.assert_called_once_with(
			basic_plugin,
			hosts = expected_hosts,
			make = mock_params["make"],
			model = mock_params["model"],
			version = mock_params["version"],
		)
		basic_plugin.owner.db.select.assert_called_once_with(ANY, (expected_hosts,))
		basic_plugin.owner.get_firmware_id.assert_called_once_with(
			make = mock_params["make"],
			model = mock_params["model"],
			version = mock_params["version"],
		)
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			[(basic_plugin.owner.db.select.return_value[0][0], basic_plugin.owner.get_firmware_id.return_value)],
			many = True,
		)

	@pytest.mark.parametrize(
		"failure_mock",
		("getHosts", "ensure_firmware_exists", "ensure_unique_mappings"),
	)
	@patch.object(target = Plugin, attribute = "ensure_unique_mappings", autospec = True)
	@patch(target = "stack.commands.add.host.firmware.mapping.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.host.firmware.mapping.plugin_basic.unique_everseen", autospec = True)
	def test_run_errors(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_ensure_unique_mappings,
		failure_mock,
		basic_plugin,
	):
		"""Test that run fails when invalid arguments or parameters are provided."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"version": "bam!", "make": "fizz", "model": "buzz"}
		expected_hosts = tuple(mock_args)
		mock_lowered.return_value = mock_params.values()
		mock_unique_everseen.return_value = mock_args
		basic_plugin.owner.getHosts.return_value = expected_hosts
		basic_plugin.owner.db.select.return_value = [["1"]]
		mock_validation_functions = {
			"getHosts": basic_plugin.owner.getHosts,
			"ensure_firmware_exists": basic_plugin.owner.ensure_firmware_exists,
			"ensure_unique_mappings": mock_ensure_unique_mappings,
		}
		mock_validation_functions[failure_mock].side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "Test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		basic_plugin.owner.db.execute.assert_not_called()
