from unittest.mock import create_autospec, ANY, patch, call
import pytest
from pymysql import IntegrityError
from stack.commands import DatabaseConnection
from stack.commands.remove.firmware import Command
from stack.exception import ArgRequired, CommandError
from stack.commands.remove.firmware.make.plugin_basic import Plugin

class TestRemoveFirmwareMakeBasicPlugin:
	"""A test case for the remove firmware make basic plugin."""

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

	def test_remove_related_models(self, basic_plugin):
		"""Test that remove_related_models works as expected."""
		mock_makes = ["foo", "bar", "baz"]
		mock_models = [["fizz"], ["buzz"]]
		expected_models = [mock_model[0] for mock_model in mock_models]
		basic_plugin.owner.db.select.return_value = mock_models

		basic_plugin.remove_related_models(makes = mock_makes)

		assert [call(ANY, make) for make in mock_makes] == basic_plugin.owner.db.select.mock_calls
		assert [
			call(command = "remove.firmware.model", args = [*expected_models, f"make={make}"]) for make in mock_makes
		] == basic_plugin.owner.call.mock_calls

	def test_remove_related_models_no_models(self, basic_plugin):
		"""Test that remove_related_models works as expected when no models exist for the makes."""
		mock_makes = ["foo", "bar", "baz"]
		mock_models = []
		basic_plugin.owner.db.select.return_value = mock_models

		basic_plugin.remove_related_models(makes = mock_makes)

		assert [call(ANY, make) for make in mock_makes] == basic_plugin.owner.db.select.mock_calls
		basic_plugin.owner.call.assert_not_called()

	@patch.object(target = Plugin, attribute = "remove_related_models", autospec = True)
	@patch(target = "stack.commands.remove.firmware.make.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.make.plugin_basic.unique_everseen", autospec = True)
	def test_run(self, mock_unique_everseen, mock_lowered, mock_remove_related_models, basic_plugin):
		"""Test that run updates the database as expected when all arguments are valid."""
		mock_args = ["foo", "bar", "baz"]
		expected_args = tuple(mock_args)
		mock_unique_everseen.return_value = (arg for arg in mock_args)

		basic_plugin.run(args = mock_args)

		basic_plugin.owner.db.execute.assert_called_once_with(ANY, (expected_args,))
		mock_lowered.assert_called_once_with(mock_args)
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.ensure_makes_exist.assert_called_once_with(makes = expected_args)
		mock_remove_related_models.assert_called_once_with(basic_plugin, makes = expected_args)

	@patch.object(target = Plugin, attribute = "remove_related_models", autospec = True)
	@patch(target = "stack.commands.remove.firmware.make.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.make.plugin_basic.unique_everseen", autospec = True)
	def test_run_makes_do_not_exist(self, mock_unique_everseen, mock_lowered, mock_remove_related_models, basic_plugin):
		"""Test that run fails if ensure makes exist fails."""
		basic_plugin.owner.ensure_makes_exist.side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = ["foo", "bar", "baz"])

		# Make sure the DB is not modified with bad arguments.
		basic_plugin.owner.db.execute.assert_not_called()
