from unittest.mock import create_autospec, patch, ANY
import pytest
from stack.commands import DatabaseConnection
from stack.commands.add.firmware import command
from stack.commands.add.firmware.version_regex.plugin_basic import Plugin
from stack.exception import ArgError, ParamError, StackError

class TestAddVersionRegexBasicPlugin:
	"""A test case for the add firmware version_regex basic plugin."""

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
		"""Make sure the plugin returns the correct provides information."""
		assert basic_plugin.provides() == "basic"

	def test_validate_args(self, basic_plugin):
		"""Test that validate_args works if the args list has one element."""
		basic_plugin.validate_args(args = ["foo"])

	@pytest.mark.parametrize("test_input", ([], ["foo", "bar"]))
	def test_validate_args_failure(self, test_input, basic_plugin):
		"""Test that validate_args fails with bad input."""
		with pytest.raises(ArgError):
			basic_plugin.validate_args(args = test_input)

	def test_validate_regex(self, basic_plugin):
		"""Test that validate_regex works if the regex provided is valid."""
		basic_plugin.validate_regex(regex = "(foo)bar")

	@pytest.mark.parametrize("test_input", ("", "(", ")", "(foobar"))
	def test_validate_regex_failure(self, test_input, basic_plugin):
		"""Test that validate_regex fails with bad input."""
		with pytest.raises(ArgError):
			basic_plugin.validate_regex(regex = test_input)

	def test_validate_name(self, basic_plugin):
		"""Test that validate_name works if the name provided is not empty and is unique."""
		basic_plugin.owner.version_regex_exists.return_value = False
		mock_name = "foo"

		basic_plugin.validate_name(name = mock_name)

		basic_plugin.owner.version_regex_exists.assert_called_once_with(name = mock_name)

	@pytest.mark.parametrize(
		"test_input, return_value",
		(
			("", False),
			("foo", True),
		)
	)
	def test_validate_name_failure(self, test_input, return_value, basic_plugin):
		"""Test that validate_name fails with bad input."""
		basic_plugin.owner.version_regex_exists.return_value = return_value

		with pytest.raises(ParamError):
			basic_plugin.validate_name(name = test_input)

	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_name", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_regex", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run(
		self,
		mock_validate_args,
		mock_validate_regex,
		mock_validate_name,
		mock_exit_stack,
		mock_unique_everseen,
		basic_plugin,
	):
		"""Test that run performs the expected action in the case where all arguments and parameters are valid."""
		mock_args = ["mock_regex"]
		# We're using uppercase to ensure that lower is used correctly when processing args and params.
		mock_models = ["MOCK_MODEL1", "MOCK_MODEL2", "MOCK_MODEL3"]
		expected_models = tuple((string.lower() for string in mock_models))
		mock_params = {
			"name": "MOCK_NAME",
			"description": "MOCK_DESCRIPTION",
			"make": "MOCK_MAKE",
			"models": ", ".join(mock_models),
		}
		expected_name = mock_params["name"].lower()
		expected_make = mock_params["make"].lower()
		basic_plugin.owner.fillParams.return_value = mock_params.values()
		mock_unique_everseen.return_value = (string for string in expected_models)

		basic_plugin.run(args = (mock_params, mock_args))

		# Make sure the params were filled with defaults.
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("name", ""),
				("description", ""),
				("make", ""),
				("models", ""),
			],
			params = mock_params,
		)
		# Expect all the validation functions to be called to validate params and args.
		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		mock_validate_regex.assert_called_once_with(basic_plugin, regex = mock_args[0])
		mock_validate_name.assert_called_once_with(basic_plugin, name = expected_name)
		# Expect the models to be made unique, forced to lowercase, and validated.
		assert expected_models == tuple(*mock_unique_everseen.call_args[0])
		basic_plugin.owner.ensure_models_exist.assert_called_once_with(
			make = expected_make,
			models = expected_models,
		)
		# Expect the DB entries to be made.
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			(mock_args[0], expected_name, mock_params["description"]),
		)
		basic_plugin.owner.call.assert_called_once_with(
			command = "set.firmware.model.version_regex",
			args = [*expected_models, f"make={expected_make}", f"version_regex={expected_name}"]
		)
		# Make sure that ExitStack was used to guard against failures.
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.version_regex",
			args = [expected_name],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()

	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_name", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_regex", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run_no_models(
		self,
		mock_validate_args,
		mock_validate_regex,
		mock_validate_name,
		mock_exit_stack,
		mock_unique_everseen,
		basic_plugin,
	):
		"""Test that run performs the expected action in the case where all arguments and parameters are valid but not models are provided."""
		mock_args = ["mock_regex"]
		# We're using uppercase to ensure that lower is used correctly when processing args and params.
		mock_params = {
			"name": "MOCK_NAME",
			"description": "MOCK_DESCRIPTION",
			"make": "MOCK_MAKE",
			"models": "",
		}
		expected_name = mock_params["name"].lower()
		expected_make = mock_params["make"].lower()
		basic_plugin.owner.fillParams.return_value = mock_params.values()

		basic_plugin.run(args = (mock_params, mock_args))

		# Make sure the params were filled with defaults.
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [
				("name", ""),
				("description", ""),
				("make", ""),
				("models", ""),
			],
			params = mock_params,
		)
		# Expect all the validation functions to be called to validate params and args.
		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		mock_validate_regex.assert_called_once_with(basic_plugin, regex = mock_args[0])
		mock_validate_name.assert_called_once_with(basic_plugin, name = expected_name)
		basic_plugin.owner.ensure_make_exists.assert_called_once_with(make = expected_make)
		# Expect the models to not be validated.
		mock_unique_everseen.assert_not_called()
		basic_plugin.owner.ensure_models_exist.assert_not_called()
		# Expect the DB entries to be made.
		basic_plugin.owner.db.execute.assert_called_once_with(
			ANY,
			(mock_args[0], expected_name, mock_params["description"]),
		)
		basic_plugin.owner.call.assert_called_once_with(
			command = "set.firmware.make.version_regex",
			args = [expected_make, f"version_regex={expected_name}"]
		)
		# Make sure that ExitStack was used to guard against failures.
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.version_regex",
			args = [expected_name],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()

	@pytest.mark.parametrize(
		"failure_mock, mock_models",
		(
			("ensure_make_exists", ""),
			("ensure_models_exist", "MOCK_MODEL1, MOCK_MODEL2, MOCK_MODEL3"),
			("validate_name", ""),
			("validate_name", "MOCK_MODEL1, MOCK_MODEL2, MOCK_MODEL3"),
			("validate_regex", ""),
			("validate_regex", "MOCK_MODEL1, MOCK_MODEL2, MOCK_MODEL3"),
			("validate_args", ""),
			("validate_args", "MOCK_MODEL1, MOCK_MODEL2, MOCK_MODEL3"),
		),
	)
	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_name", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_regex", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run_validation_errors(
		self,
		mock_validate_args,
		mock_validate_regex,
		mock_validate_name,
		mock_exit_stack,
		mock_unique_everseen,
		failure_mock,
		mock_models,
		basic_plugin,
	):
		"""Test that run fails when the parameters do not validate."""
		mock_args = ["mock_regex"]
		mock_params = {
			"name": "MOCK_NAME",
			"description": "MOCK_DESCRIPTION",
			"make": "MOCK_MAKE",
			"models": mock_models,
		}
		basic_plugin.owner.fillParams.return_value = mock_params.values()
		validation_function_mocks = {
			"validate_args": mock_validate_args,
			"validate_regex": mock_validate_regex,
			"validate_name": mock_validate_name,
			"ensure_make_exists": basic_plugin.owner.ensure_make_exists,
			"ensure_models_exist": basic_plugin.owner.ensure_models_exist,
		}
		# Set the appropriate mock call to fail
		validation_function_mocks[failure_mock].side_effect = StackError("Test error")

		with pytest.raises(StackError):
			basic_plugin.run(args = (mock_params, mock_args))

		# Make sure the database calls are not made if the arguments don't validate
		basic_plugin.owner.db.execute.assert_not_called()

	@pytest.mark.parametrize("mock_models", ("", "MOCK_MODEL1, MOCK_MODEL2, MOCK_MODEL3"))
	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.unique_everseen", autospec = True)
	@patch(target = "stack.commands.add.firmware.version_regex.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_name", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_regex", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run_set_relation_fails(
		self,
		mock_validate_args,
		mock_validate_regex,
		mock_validate_name,
		mock_exit_stack,
		mock_unique_everseen,
		mock_models,
		basic_plugin,
	):
		"""Test that run fails and cleans up when setting the relation to the make or model fails."""
		mock_args = ["mock_regex"]
		mock_params = {
			"name": "MOCK_NAME",
			"description": "MOCK_DESCRIPTION",
			"make": "MOCK_MAKE",
			"models": mock_models,
		}
		basic_plugin.owner.fillParams.return_value = mock_params.values()
		basic_plugin.owner.call.side_effect = StackError("Test error")

		with pytest.raises(StackError):
			basic_plugin.run(args = (mock_params, mock_args))

		# Make sure the cleanup is setup to be run, and don't expect it to be dismissed because of the error.
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.version_regex",
			args = [mock_params["name"].lower()],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_not_called()
