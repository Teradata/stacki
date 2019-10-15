from unittest.mock import create_autospec, ANY, patch
import pytest
from pymysql import IntegrityError
from stack.commands import DatabaseConnection
from stack.commands.remove.firmware import Command
from stack.exception import ArgRequired, CommandError
from stack.commands.remove.firmware.imp.plugin_basic import Plugin

class TestRemoveFirmwareImpBasicPlugin:
	"""A test case for the remove firmware make version_regex basic plugin."""

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

	@patch(target = "stack.commands.remove.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.imp.plugin_basic.unique_everseen", autospec = True)
	def test_run(self, mock_unique_everseen, mock_lowered, basic_plugin):
		"""Test that run updates the database as expected when all arguments are valid."""
		mock_args = ["foo", "bar", "baz"]
		expected_args = tuple(mock_args)
		mock_unique_everseen.return_value = (arg for arg in mock_args)

		basic_plugin.run(args = mock_args)

		basic_plugin.owner.db.execute.assert_called_once_with(ANY, (expected_args,))
		mock_lowered.assert_called_once_with(mock_args)
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.ensure_imps_exist.assert_called_once_with(imps = expected_args)

	@patch(target = "stack.commands.remove.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.imp.plugin_basic.unique_everseen", autospec = True)
	def test_run_imps_do_not_exist(self, mock_unique_everseen, mock_lowered, basic_plugin):
		"""Test that run fails if ensure imps exist fails."""
		basic_plugin.owner.ensure_imps_exist.side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = ["foo", "bar", "baz"])

		# Make sure the DB is not modified with bad arguments.
		basic_plugin.owner.db.execute.assert_not_called()

	@patch(target = "stack.commands.remove.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.imp.plugin_basic.unique_everseen", autospec = True)
	def test_run_integrity_error(self, mock_unique_everseen, mock_lowered, basic_plugin):
		"""Test that run fails if there is an integrity error and turns it into a command error."""
		basic_plugin.owner.db.execute.side_effect = IntegrityError("Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = ["foo", "bar", "baz"])
