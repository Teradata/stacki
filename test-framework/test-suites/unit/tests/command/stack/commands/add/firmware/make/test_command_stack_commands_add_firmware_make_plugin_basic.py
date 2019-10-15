from unittest.mock import create_autospec, patch, ANY
import pytest
from stack.commands import DatabaseConnection
from stack.commands.add.firmware import Command
from stack.commands.add.firmware.make.plugin_basic import Plugin
from stack.exception import CommandError

class TestAddMakeBasicPlugin:
	"""A test case for the add firmware make basic plugin."""

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
		"""Make sure the plugin returns the correct provides information."""
		assert basic_plugin.provides() == "basic"

	@patch(target = "stack.commands.add.firmware.make.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.make.plugin_basic.unique_everseen", autospec = True)
	def test_run(
		self,
		mock_unique_everseen,
		mock_lowered,
		basic_plugin,
	):
		"""Test that run modifies the database as expected when all the args are valid."""
		expected_makes = ("foo", "bar", "baz")
		mock_args = [*expected_makes]
		mock_unique_everseen.return_value = (arg for arg in mock_args)

		basic_plugin.run(args = mock_args)

		# Make sure the arguments were validated.
		mock_lowered.assert_called_once_with(mock_args)
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.ensure_unique_makes.assert_called_once_with(
			makes = expected_makes,
		)
		# Expect the database to be updated
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			[(expected_make,) for expected_make in expected_makes],
			many = True,
		)

	@patch(target = "stack.commands.add.firmware.make.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.make.plugin_basic.unique_everseen", autospec = True)
	def test_run_error(
		self,
		mock_unique_everseen,
		mock_lowered,
		basic_plugin,
	):
		"""Test that run fails when argument validation fails and does not touch the database."""
		expected_makes = ("foo", "bar", "baz")
		mock_args = [*expected_makes]
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		basic_plugin.owner.ensure_unique_makes.side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "Test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.run(args = mock_args)

		# Expect the database to be untouched
		basic_plugin.owner.db.execute.assert_not_called()
