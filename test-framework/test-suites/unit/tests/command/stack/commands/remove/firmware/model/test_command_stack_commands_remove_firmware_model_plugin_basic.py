from unittest.mock import create_autospec, ANY, patch, call
import pytest
from pymysql import IntegrityError
from stack.commands import DatabaseConnection
from stack.commands.remove.firmware import Command
from stack.exception import ArgRequired, CommandError
from stack.commands.remove.firmware.model.plugin_basic import Plugin

class TestRemoveFirmwareModelBasicPlugin:
	"""A test case for the remove firmware model basic plugin."""

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

	def test_remove_related_firmware(self, basic_plugin):
		"""Test that remove_related_firmware works as expected."""
		mock_make = "bam!"
		mock_models = ["foo", "bar", "baz"]
		mock_firmwares = [["fizz"], ["buzz"]]
		expected_firmwares = [mock_firmware[0] for mock_firmware in mock_firmwares]
		basic_plugin.owner.db.select.return_value = mock_firmwares

		basic_plugin.remove_related_firmware(make = mock_make, models = mock_models)

		assert [call(ANY, (mock_make, model)) for model in mock_models] == basic_plugin.owner.db.select.mock_calls
		assert [
			call(
				command = "remove.firmware",
				args = [*expected_firmwares, f"make={mock_make}", f"model={model}"],
			)
			for model in mock_models
		] == basic_plugin.owner.call.mock_calls

	def test_remove_related_firmware_no_firmware(self, basic_plugin):
		"""Test that remove_related_firmware works as expected when there are no related firmwares."""
		mock_make = "bam!"
		mock_models = ["foo", "bar", "baz"]
		mock_firmwares = []
		basic_plugin.owner.db.select.return_value = mock_firmwares

		basic_plugin.remove_related_firmware(make = mock_make, models = mock_models)

		assert [call(ANY, (mock_make, model)) for model in mock_models] == basic_plugin.owner.db.select.mock_calls
		basic_plugin.owner.call.assert_not_called()

	@patch.object(target = Plugin, attribute = "remove_related_firmware", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.plugin_basic.unique_everseen", autospec = True)
	def test_run(self, mock_unique_everseen, mock_lowered, mock_remove_related_firmware, basic_plugin):
		"""Test that run updates the database as expected when all arguments are valid."""
		mock_args = ["foo", "bar", "baz"]
		expected_args = tuple(mock_args)
		mock_params = {"make": "fizz"}
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		mock_lowered.return_value = mock_params.values()

		basic_plugin.run(args = (mock_params, mock_args))

		basic_plugin.owner.db.execute.assert_called_once_with(ANY, (expected_args, mock_params["make"]))
		assert [call(basic_plugin.owner.fillParams.return_value), call(mock_args)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.ensure_models_exist.assert_called_once_with(
			make = mock_params["make"],
			models = expected_args,
		)
		mock_remove_related_firmware.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			models = expected_args,
		)

	@patch.object(target = Plugin, attribute = "remove_related_firmware", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.plugin_basic.unique_everseen", autospec = True)
	def test_run_models_do_not_exist(self, mock_unique_everseen, mock_lowered, mock_remove_related_firmware, basic_plugin):
		"""Test that run fails if ensure models exist fails."""
		mock_args = ["foo", "bar", "baz"]
		expected_args = tuple(mock_args)
		mock_params = {"make": "fizz"}
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		mock_lowered.return_value = mock_params.values()
		basic_plugin.owner.ensure_models_exist.side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		# model sure the DB is not modified with bad arguments.
		basic_plugin.owner.db.execute.assert_not_called()
