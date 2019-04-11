from unittest.mock import create_autospec, ANY, patch, call
import pytest
from stack.commands import DatabaseConnection
from stack.commands.set.firmware.model.version_regex import Command
from stack.exception import CommandError
from stack.commands.set.firmware.model.version_regex.plugin_basic import Plugin

class TestSetFirmwareModelVersionRegexBasicPlugin:
	"""A test case for the set firmware model version_regex basic plugin."""

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
		"""Ensure that provides returns 'basic'."""
		assert basic_plugin.provides() == "basic"

	@patch(target = "stack.commands.set.firmware.model.version_regex.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.set.firmware.model.version_regex.plugin_basic.unique_everseen", autospec = True)
	def test_run(self, mock_unique_everseen, mock_lowered, basic_plugin):
		"""Test that run updates the database as expected when all arguments are valid."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"make": "mock_make", "version_regex": "mock_name"}
		expected_args = tuple(mock_args)
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		mock_lowered.return_value = mock_params.values()

		basic_plugin.run(args = (mock_params, mock_args))

		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			(basic_plugin.owner.get_version_regex_id.return_value, expected_args, mock_params["make"]),
		)
		basic_plugin.owner.get_version_regex_id.assert_called_once_with(name = mock_params["version_regex"])
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [("make", ""), ("version_regex", "")],
			params = mock_params,
		)
		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.ensure_models_exist.assert_called_once_with(make = mock_params["make"], models = expected_args)
		basic_plugin.owner.ensure_version_regex_exists.assert_called_once_with(name = mock_params["version_regex"])

	@pytest.mark.parametrize("failure_mock", ("ensure_models_exist", "ensure_version_regex_exists"))
	@patch(target = "stack.commands.set.firmware.model.version_regex.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.set.firmware.model.version_regex.plugin_basic.unique_everseen", autospec = True)
	def test_run_missing_args(self, mock_unique_everseen, mock_lowered, failure_mock, basic_plugin):
		"""Test that run fails when any of the exist* functions fail."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"make": "mock_make", "version_regex": "mock_name"}
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		mock_lowered.return_value = mock_params.values()
		mock_validation_functions = {
			"ensure_models_exist": basic_plugin.owner.ensure_models_exist,
			"ensure_version_regex_exists": basic_plugin.owner.ensure_version_regex_exists,
		}
		mock_validation_functions[failure_mock].side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		# model sure the DB is not modified with bad arguments.
		basic_plugin.owner.db.execute.assert_not_called()
