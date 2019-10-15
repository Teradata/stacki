from unittest.mock import create_autospec, ANY, patch, call
import pytest
from pymysql import IntegrityError
from stack.commands import DatabaseConnection
from stack.commands.remove.firmware import Command
from stack.exception import ArgRequired, CommandError
from stack.commands.remove.firmware.plugin_basic import Plugin

class TestRemoveFirmwareBasicPlugin:
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

	@pytest.mark.parametrize(
		"make, model, versions",
		(
			("", "", []),
			("foo", "", []),
			("foo", "bar", []),
			("foo", "bar", ["fizz", "buzz"])
		),
	)
	def test_validate_inputs(self, make, model, versions, basic_plugin):
		"""Test that validate inputs works as expected when all inputs are valid."""
		basic_plugin.validate_inputs(make = make, model = model, versions = versions)

		if make:
			basic_plugin.owner.ensure_make_exists.assert_called_once_with(
				make = make,
			)
		else:
			basic_plugin.owner.ensure_make_exists.assert_not_called()

		if model:
			basic_plugin.owner.ensure_model_exists.assert_called_once_with(
				make = make,
				model = model,
			)
		else:
			basic_plugin.owner.ensure_model_exists.assert_not_called()

		if versions:
			basic_plugin.owner.ensure_firmwares_exist.assert_called_once_with(
				make = make,
				model = model,
				versions = versions,
			)
		else:
			basic_plugin.owner.ensure_firmwares_exist.assert_not_called()

	@pytest.mark.parametrize("failure_mock", ("ensure_make_exists", "ensure_model_exists", "ensure_firmwares_exist"))
	def test_validate_inputs_errors(self, failure_mock, basic_plugin):
		"""Test that validate inputs works as expected when all inputs are valid."""
		mock_validation_functions = {
			"ensure_make_exists": basic_plugin.owner.ensure_make_exists,
			"ensure_model_exists": basic_plugin.owner.ensure_model_exists,
			"ensure_firmwares_exist": basic_plugin.owner.ensure_firmwares_exist,
		}
		mock_validation_functions[failure_mock].side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.validate_inputs(make = "foo", model = "bar", versions = ["baz"])

	@pytest.mark.parametrize(
		"mock_make, mock_model, mock_versions, expected_query_params",
		(
			("", "", [], []),
			("foo", "", [], ["foo"]),
			("foo", "bar", [], ["foo", "bar"]),
			("foo", "bar", ["fizz", "buzz"], [["fizz", "buzz"], "foo", "bar"]),
		),
	)
	def test_build_query(
		self,
		mock_make,
		mock_model,
		mock_versions,
		expected_query_params,
		basic_plugin,
	):
		"""Test that build query builds up the query as expected based on input arguments."""
		query, query_params = basic_plugin.build_query(
			make = mock_make,
			model = mock_model,
			versions = mock_versions,
		)

		assert expected_query_params == query_params

	@patch.object(target = Plugin, attribute = "build_query", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_inputs", autospec = True)
	@patch(target = "stack.commands.remove.firmware.plugin_basic.Path", autospec = True)
	@patch(target = "stack.commands.remove.firmware.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.remove.firmware.plugin_basic.lowered", autospec = True)
	def test_run(
		self,
		mock_lowered,
		mock_unique_everseen,
		mock_path,
		mock_validate_inputs,
		mock_build_query,
		basic_plugin,
	):
		"""Test that run works as expected when the params and args are valid."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"make": "fizz", "model": "buzz"}
		expected_versions = tuple(mock_args)
		mock_unique_everseen.return_value = expected_versions
		mock_lowered.return_value = mock_params.values()
		mock_query = "amockquery"
		mock_query_params = ["aparam", "anotherparam"]
		mock_build_query.return_value = (mock_query, mock_query_params)
		basic_plugin.owner.db.select.return_value = [["id", "path"]]

		basic_plugin.run(args = (mock_params, mock_args))

		assert [call(mock_args), call(basic_plugin.owner.fillParams.return_value)] == mock_lowered.mock_calls
		mock_unique_everseen.assert_called_once_with(mock_lowered.return_value)
		mock_validate_inputs.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			model = mock_params["model"],
			versions = expected_versions,
		)
		mock_build_query.assert_called_once_with(
			basic_plugin,
			make = mock_params["make"],
			model = mock_params["model"],
			versions = expected_versions,
		)
		basic_plugin.owner.db.select.assert_called_once_with(mock_query, mock_query_params)
		chained = call(basic_plugin.owner.db.select.return_value[0][1]).resolve(strict = True).unlink()
		assert chained.call_list() == mock_path.mock_calls
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			basic_plugin.owner.db.select.return_value[0][0],
		)

	@patch.object(target = Plugin, attribute = "build_query", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_inputs", autospec = True)
	@patch(target = "stack.commands.remove.firmware.plugin_basic.Path", autospec = True)
	@patch(target = "stack.commands.remove.firmware.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.remove.firmware.plugin_basic.lowered", autospec = True)
	def test_run_errors(
		self,
		mock_lowered,
		mock_unique_everseen,
		mock_path,
		mock_validate_inputs,
		mock_build_query,
		basic_plugin,
	):
		"""Test that run fails when params and/or args are invalid."""
		mock_args = ["foo", "bar", "baz"]
		mock_params = {"make": "fizz", "model": "buzz"}
		expected_versions = tuple(mock_args)
		mock_unique_everseen.return_value = expected_versions
		mock_lowered.return_value = mock_params.values()
		mock_query = "amockquery"
		mock_query_params = ["aparam", "anotherparam"]
		mock_build_query.return_value = (mock_query, mock_query_params)
		basic_plugin.owner.db.select.return_value = [["id", "path"]]
		mock_validate_inputs.side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))
