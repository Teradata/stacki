from unittest.mock import create_autospec, ANY, patch, MagicMock, call
import pytest
from stack.commands import DatabaseConnection
from stack.commands.remove.firmware import command
from stack.exception import ArgRequired, ParamRequired, ParamError, CommandError
from stack.commands.remove.firmware.model.version_regex.plugin_basic import Plugin

class TestRemoveFirmwareModelVersionRegexBasicPlugin:
	"""A test case for the remove firmware model version_regex basic plugin."""

	@pytest.fixture
	def basic_plugin(self):
		"""A fixture that returns the plugin instance for use in tests.

		This sets up the required mocks needed to construct the plugin class.
		"""
		mock_command = create_autospec(
			spec = command,
			instance = True,
		)
		mock_command.db = create_autospec(
			spec = DatabaseConnection,
			spec_set = True,
			instance = True,
		)
		return Plugin(command = mock_command)

	def test_provides(self, basic_plugin):
		"""Ensure that provides returns "basic"."""
		assert basic_plugin.provides() == "basic"

	def test_validate_args(self, basic_plugin):
		"""Test that validate args works when args are provided."""
		basic_plugin.validate_args(args = ["foo", "bar", "baz"])

	def test_validate_args_error(self, basic_plugin):
		"""Test that validate args fails when args are not provided."""
		with pytest.raises(ArgRequired):
			basic_plugin.validate_args(args = [])

	def test_validate_make(self, basic_plugin):
		"""Test that validate_make works when the make name is provided and the make exists in the database."""
		basic_plugin.owner.make_exists.return_value = True
		mock_make = "foo"

		basic_plugin.validate_make(make = mock_make)

		basic_plugin.owner.make_exists.assert_called_once_with(make = mock_make)

	def test_validate_make_empty_string(self, basic_plugin):
		"""Test that validate_make fails when the make name is an empty string."""
		with pytest.raises(ParamRequired):
			basic_plugin.validate_make(make = "")

	def test_validate_make_not_in_database(self, basic_plugin):
		"""Test that validate_make fails when the make name is not present in the database."""
		basic_plugin.owner.make_exists.return_value = False

		with pytest.raises(ParamError):
			basic_plugin.validate_make(make = "foo")

	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.version_regex.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.version_regex.plugin_basic.unique_everseen", autospec = True)
	def test_run(self, mock_unique_everseen, mock_lowered, mock_validate_args, mock_validate_make, basic_plugin):
		"""Test that run updates the database as expected when all arguments are valid."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"make": "fizz"}
		expected_args = tuple(mock_args)
		expected_param = mock_params["make"]
		mock_unique_everseen.return_value = (arg for arg in mock_args)
		# Since we don't care about the first return value, as it should be passed directly into unique_everseen(),
		# we just use a MagicMock so we can do equality testing later in assert_called_once_with().
		first_lowered_return = MagicMock()
		mock_lowered.side_effect = (
			first_lowered_return,
			(make for make in mock_params.values()),
		)

		basic_plugin.run(args = (mock_params, mock_args))

		# Ensure that the database update was performed
		basic_plugin.owner.db.execute.assert_called_once_with(ANY, (expected_args, expected_param))
		# Ensure that the expected calls happened for validating args and params.
		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(first_lowered_return)
		basic_plugin.owner.ensure_models_exist.assert_called_once_with(models = expected_args, make = expected_param)
		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		mock_validate_make.assert_called_once_with(basic_plugin, make = expected_param)

	@pytest.mark.parametrize("failure_mock", ("validate_args", "validate_make", "ensure_models_exist"))
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.version_regex.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.remove.firmware.model.version_regex.plugin_basic.unique_everseen", autospec = True)
	def test_run_errors(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_args,
		mock_validate_make,
		failure_mock,
		basic_plugin,
	):
		"""Test that run fails if the arguments do not validate."""
		mock_validation_functions = {
			"validate_args": mock_validate_args,
			"validate_make": mock_validate_make,
			"ensure_models_exist": basic_plugin.owner.ensure_models_exist,
		}
		# Set the appropriate mock function to fail.
		mock_validation_functions[failure_mock].side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test failure")
		mock_lowered.return_value = ("foo",)

		with pytest.raises(CommandError):
			basic_plugin.run(args = ({"foo": "bar"}, ["baz"]))

		# Ensure that the database update was not performed due to argument and/or param errors
		basic_plugin.owner.db.execute.assert_not_called()
