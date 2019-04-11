from unittest.mock import create_autospec, patch, ANY, call
import pytest
from contextlib import ExitStack
from stack.commands import DatabaseConnection
from stack.commands.add.firmware import Command
from stack.commands.add.firmware.model.plugin_basic import Plugin
from stack.exception import CommandError

class TestAddFirmwareModelBasicPlugin:
	"""A test case for the add firmware model basic plugin."""

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

	def test_create_missing_make(self, basic_plugin):
		"""Test that create missing make works as expected when the make doesn't exist."""
		basic_plugin.owner.make_exists.return_value = False
		mock_exit_stack = create_autospec(
			spec = ExitStack,
			spec_set = True,
		)
		mock_make = "foo"

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_make(make = mock_make, cleanup = mock_cleanup)

		basic_plugin.owner.make_exists.assert_called_once_with(make = mock_make)
		basic_plugin.owner.call.assert_called_once_with(command = "add.firmware.make", args = [mock_make])
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.make",
			args = [mock_make],
		)

	def test_create_missing_make_make_exists(self, basic_plugin):
		"""Test that create missing make works as expected when the make exists."""
		basic_plugin.owner.make_exists.return_value = True
		mock_exit_stack = create_autospec(
			spec = ExitStack,
			spec_set = True,
		)
		mock_make = "foo"

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_make(make = mock_make, cleanup = mock_cleanup)

		basic_plugin.owner.make_exists.assert_called_once_with(make = mock_make)
		basic_plugin.owner.call.assert_not_called()
		mock_exit_stack.return_value.__enter__.return_value.assert_not_called()

	def test_create_missing_imp(self, basic_plugin):
		"""Test that create missing imp works as expected when the imp doesn't exist."""
		basic_plugin.owner.imp_exists.return_value = False
		mock_exit_stack = create_autospec(
			spec = ExitStack,
			spec_set = True,
		)
		mock_imp = "foo"

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_imp(imp = mock_imp, cleanup = mock_cleanup)

		basic_plugin.owner.imp_exists.assert_called_once_with(imp = mock_imp)
		basic_plugin.owner.call.assert_called_once_with(command = "add.firmware.imp", args = [mock_imp])
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.imp",
			args = [mock_imp],
		)

	def test_create_missing_imp_make_exists(self, basic_plugin):
		"""Test that create missing imp works as expected when the imp exists."""
		basic_plugin.owner.imp_exists.return_value = True
		mock_exit_stack = create_autospec(
			spec = ExitStack,
			spec_set = True,
		)
		mock_imp = "foo"

		with mock_exit_stack() as mock_cleanup:
			basic_plugin.create_missing_imp(imp = mock_imp, cleanup = mock_cleanup)

		basic_plugin.owner.imp_exists.assert_called_once_with(imp = mock_imp)
		basic_plugin.owner.call.assert_not_called()
		mock_exit_stack.return_value.__enter__.return_value.assert_not_called()

	@patch.object(target = Plugin, attribute = "create_missing_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "create_missing_make", autospec = True)
	@patch(target = "stack.commands.add.firmware.model.plugin_basic.ExitStack", autospec = True)
	@patch(target = "stack.commands.add.firmware.model.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.model.plugin_basic.unique_everseen", autospec = True)
	def test_run(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_exit_stack,
		mock_create_missing_make,
		mock_create_missing_imp,
		basic_plugin,
	):
		"""Test that run modifies the database as expected when all the args are valid."""
		expected_models = ("foo", "bar", "baz")
		mock_args = [*expected_models]
		mock_params = {"make": "fizz", "imp": "buzz"}
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		mock_lowered.return_value = mock_params.values()

		basic_plugin.run(args = (mock_params, mock_args))

		# model sure the arguments were validated.
		assert [call(basic_plugin.owner.fillParams.return_value), call(mock_args)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.ensure_unique_models.assert_called_once_with(
			models = expected_models,
			make = mock_params["make"],
		)
		# Expect the make and imp to be created if needed
		mock_create_missing_make.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			cleanup = mock_exit_stack.return_value.__enter__.return_value,
		)
		mock_create_missing_imp.assert_called_once_with(
			basic_plugin,
			mock_params["imp"],
			cleanup = mock_exit_stack.return_value.__enter__.return_value,
		)
		# Expect the IDs of the imp and make to be fetched.
		basic_plugin.owner.get_make_id.assert_called_once_with(make = mock_params["make"])
		basic_plugin.owner.get_imp_id.assert_called_once_with(imp = mock_params["imp"])
		# Expect the database to be updated
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			[
				(
					model,
					basic_plugin.owner.get_make_id.return_value,
					basic_plugin.owner.get_imp_id.return_value,
				)
				for model in expected_models
			],
			many = True,
		)
		# Expect cleanup to be dismissed.
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()

	@pytest.mark.parametrize(
		"mock_make, mock_imp, side_effect",
		(
			("", "bar", None),
			("foo", "", None),
			("foo", "bar", CommandError(cmd = None, msg = "Test message")),
		)
	)
	@patch.object(target = Plugin, attribute = "create_missing_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "create_missing_make", autospec = True)
	@patch(target = "stack.commands.add.firmware.model.plugin_basic.ExitStack", autospec = True)
	@patch(target = "stack.commands.add.firmware.model.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.model.plugin_basic.unique_everseen", autospec = True)
	def test_run_errors(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_exit_stack,
		mock_create_missing_make,
		mock_create_missing_imp,
		mock_make,
		mock_imp,
		side_effect,
		basic_plugin,
	):
		"""Test that run fails when the arguments or parameters are invalid and does not touch the database."""
		expected_models = ("foo", "bar", "baz")
		mock_args = [*expected_models]
		mock_params = {"make": mock_make, "imp": mock_imp}
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		mock_lowered.return_value = mock_params.values()
		basic_plugin.owner.ensure_unique_models.side_effect = side_effect

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		# Expect the database to not be touched
		basic_plugin.owner.db.execute.assert_not_called()
