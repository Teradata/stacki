from unittest.mock import create_autospec, ANY, patch, call
import pytest
from stack.commands import DatabaseConnection
from stack.commands.list.firmware import Command
from stack.commands.list.firmware.model.plugin_basic import Plugin
from stack.exception import CommandError

class TestListFirmwareModelBasicPlugin:
	"""A test case for the list firmware model basic plugin."""

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

	def test_validate_make(self, basic_plugin):
		"""Test that validate make works as expected in the case where a make is provided."""
		mock_make = "foo"

		basic_plugin.validate_make(make = mock_make)

		basic_plugin.owner.ensure_make_exists.assert_called_once_with(make = mock_make)

	def test_validate_make_skip(self, basic_plugin):
		"""Test that validate make works as expected in the case where a make is not provided."""
		mock_make = ""

		basic_plugin.validate_make(make = mock_make)

		basic_plugin.owner.ensure_make_exists.assert_not_called()

	def test_validate_make_error(self, basic_plugin):
		"""Test that validate fails when ensuring the make exists fails."""
		mock_make = "foo"
		basic_plugin.owner.ensure_make_exists.side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "Test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.validate_make(make = mock_make)

	def test_validate_models(self, basic_plugin):
		"""Test that validate models works as expected in the case where a make and some models are provided."""
		mock_make = "foo"
		mock_models = ["bar", "baz"]

		basic_plugin.validate_models(make = mock_make, models = mock_models)

		basic_plugin.owner.ensure_models_exist.assert_called_once_with(make = mock_make, models = mock_models)

	def test_validate_models_skip(self, basic_plugin):
		"""Test that validate models works as expected in the case where models are not provided."""
		mock_make = "foo"
		mock_models = []

		basic_plugin.validate_models(make = mock_make, models = mock_models)

		basic_plugin.owner.ensure_models_exist.assert_not_called()

	def test_validate_models_error(self, basic_plugin):
		"""Test that validate fails when ensuring the models exist fails."""
		mock_make = "foo"
		mock_models = ["bar", "baz"]
		basic_plugin.owner.ensure_models_exist.side_effect = CommandError(
			cmd = basic_plugin.owner,
			msg = "Test error",
		)

		with pytest.raises(CommandError):
			basic_plugin.validate_models(make = mock_make, models = mock_models)

	@pytest.mark.parametrize(
		"make, models, expected",
		(
			("foo", ["bar", "baz"], [["bar", "baz"], "foo"]),
			("foo", [], ["foo"]),
			("", [], []),
		)
	)
	def test_get_expanded_results(self, make, models, expected, basic_plugin):
		"""Test that get expanded results is called as expected based on the provided args."""
		basic_plugin.owner.db.select.return_value = [
			["foo", "bar", "baz", "bag"],
			["fizz", "buzz", "bizz", "bam!"],
		]
		expected_results = {
			"keys": ["make", "model", "implementation", "version_regex_name"],
			"values": [(row[0], row[1:]) for row in basic_plugin.owner.db.select.return_value],
		}

		assert expected_results == basic_plugin.get_expanded_results(make = make, models = models)

		basic_plugin.owner.db.select.assert_called_once_with(ANY, expected)

	@pytest.mark.parametrize(
		"make, models, expected",
		(
			("foo", ["bar", "baz"], [["bar", "baz"], "foo"]),
			("foo", [], ["foo"]),
			("", [], []),
		)
	)
	def test_get_results(self, make, models, expected, basic_plugin):
		"""Test that get results is called as expected based on the provided args."""
		basic_plugin.owner.db.select.return_value = [
			["foo", "bar", "baz", "bag"],
			["fizz", "buzz", "bizz", "bam!"],
		]
		expected_results = {
			"keys": ["make", "model", "implementation", "version_regex_name"],
			"values": [(row[0], row[1:]) for row in basic_plugin.owner.db.select.return_value],
		}

		assert expected_results == basic_plugin.get_expanded_results(make = make, models = models)

		basic_plugin.owner.db.select.assert_called_once_with(ANY, expected)

	@patch.object(target = Plugin, attribute = "get_results", autospec = True)
	@patch.object(target = Plugin, attribute = "get_expanded_results", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_models", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch(target = "stack.commands.list.firmware.model.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.list.firmware.model.plugin_basic.unique_everseen", autospec = True)
	def test_run(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_make,
		mock_validate_models,
		mock_get_expanded_results,
		mock_get_results,
		basic_plugin,
	):
		"""Test that run works as expected when expanded is True."""
		mock_args = ["foo", "bar", "baz"]
		expected_args = tuple(mock_args)
		mock_params = {"expanded": "true", "make": "fizz"}
		mock_unique_everseen.return_value = mock_args
		mock_lowered.return_value = mock_params.values()
		basic_plugin.owner.str2bool.return_value = True

		basic_plugin.run(args = (mock_params, mock_args))

		# Ensure the params and args were processed and validated as expected
		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [("expanded", "false"), ("make", "")],
			params = mock_params,
		)
		basic_plugin.owner.str2bool.assert_called_once_with(mock_params["expanded"])
		mock_validate_make.assert_called_once_with(basic_plugin, make = mock_params["make"])
		mock_validate_models.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			models = expected_args,
		)
		# Since expanded was True, ensure that we called the right function to get the expanded results.
		mock_get_expanded_results.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			models = expected_args,
		)
		mock_get_results.assert_not_called()

	@patch.object(target = Plugin, attribute = "get_results", autospec = True)
	@patch.object(target = Plugin, attribute = "get_expanded_results", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_models", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_make", autospec = True)
	@patch(target = "stack.commands.list.firmware.model.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.list.firmware.model.plugin_basic.unique_everseen", autospec = True)
	def test_run_expanded_false(
		self,
		mock_unique_everseen,
		mock_lowered,
		mock_validate_make,
		mock_validate_models,
		mock_get_expanded_results,
		mock_get_results,
		basic_plugin,
	):
		"""Test that run works as expected when expanded is False."""
		mock_args = ["foo", "bar", "baz"]
		expected_args = tuple(mock_args)
		mock_params = {"expanded": "false", "make": "fizz"}
		mock_unique_everseen.return_value = mock_args
		mock_lowered.return_value = mock_params.values()
		basic_plugin.owner.str2bool.return_value = False

		basic_plugin.run(args = (mock_params, mock_args))

		# Ensure the params and args were processed and validated as expected
		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [("expanded", "false"), ("make", "")],
			params = mock_params,
		)
		basic_plugin.owner.str2bool.assert_called_once_with(mock_params["expanded"])
		mock_validate_make.assert_called_once_with(basic_plugin, make = mock_params["make"])
		mock_validate_models.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			models = expected_args,
		)
		# Since expanded was True, ensure that we called the right function to get the expanded results.
		mock_get_expanded_results.assert_not_called()
		mock_get_results.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			models = expected_args,
		)
