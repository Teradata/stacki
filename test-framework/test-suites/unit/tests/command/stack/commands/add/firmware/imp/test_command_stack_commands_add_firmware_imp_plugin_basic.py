from unittest.mock import create_autospec, patch, ANY
import pytest
import stack.commands.list.host.firmware
import stack.commands.sync.host.firmware
from stack.commands import DatabaseConnection
from stack.commands.add.firmware import Command
from stack.commands.add.firmware.imp.plugin_basic import Plugin
from stack.exception import ArgError, ParamError, CommandError

class TestAddImpBasicPlugin:
	"""A test case for the add firmware imp basic plugin."""

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

	def test_validate_args(self, basic_plugin):
		"""Test that validate_args works if the args list has one element."""
		basic_plugin.validate_args(args = ["foo"])

	@pytest.mark.parametrize("test_input", ([], ["foo", "bar"]))
	def test_validate_args_failure(self, test_input, basic_plugin):
		"""Test that validate_args fails with bad input."""
		with pytest.raises(ArgError):
			basic_plugin.validate_args(args = test_input)

	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.Path", autospec = True)
	@patch(target = "inspect.getsourcefile", autospec = True)
	def test_validate_imp(self, mock_getsourcefile, mock_path, basic_plugin):
		"""Test that validate_imp works when the imp doesn't already exist in the database and the files are found on disk."""
		basic_plugin.owner.imp_exists.return_value = False
		mock_path.return_value.parent.resolve.return_value.__truediv__.return_value.exists.return_value = True
		mock_imp = "foo"

		basic_plugin.validate_imp(imp = mock_imp)

		# Make sure the database was checked for duplicates.
		basic_plugin.owner.imp_exists.assert_called_once_with(imp = mock_imp)
		# Make sure the files were checked for existence on disk.
		mock_getsourcefile.assert_any_call(stack.commands.list.host.firmware)
		mock_getsourcefile.assert_any_call(stack.commands.sync.host.firmware)
		mock_path.assert_any_call(mock_getsourcefile.return_value)
		mock_path.return_value.parent.resolve.return_value.__truediv__.return_value.exists.assert_called_with()

	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.Path", autospec = True)
	@patch(target = "inspect.getsourcefile", autospec = True)
	def test_validate_imp_already_exists(self, mock_getsourcefile, mock_path, basic_plugin):
		"""Test that validate_imp fails when the implementation already exists in the database."""
		basic_plugin.owner.imp_exists.return_value = True
		mock_path.return_value.parent.resolve.return_value.__truediv__.return_value.exists.return_value = True
		mock_imp = "foo"

		with pytest.raises(ArgError):
			basic_plugin.validate_imp(imp = mock_imp)

	@pytest.mark.parametrize("return_values", ((True, False), (False, True), (False, False)))
	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.Path", autospec = True)
	@patch(target = "inspect.getsourcefile", autospec = True)
	def test_validate_imp_missing_files(self, mock_getsourcefile, mock_path, return_values, basic_plugin):
		"""Test that validate_imp fails when the implementation files are missing from the filesystem."""
		basic_plugin.owner.imp_exists.return_value = False
		mock_path.return_value.parent.resolve.return_value.__truediv__.return_value.exists.side_effect = return_values
		mock_imp = "foo"

		with pytest.raises(ArgError):
			basic_plugin.validate_imp(imp = mock_imp)

	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run(
		self,
		mock_validate_args,
		mock_validate_imp,
		mock_exit_stack,
		mock_lowered,
		basic_plugin,
	):
		"""Test that run modifies the database as expected when all the params and args are valid."""
		expected_imp = "foo"
		mock_args = [expected_imp]
		expected_models = ["baz", "fizz", "buzz"]
		mock_params = {"make": "bar", "models": ", ".join(expected_models)}
		mock_lowered.return_value = (param for param in mock_params.values())

		basic_plugin.run(args = (mock_params, mock_args))

		# Make sure the arguments and parameters were validated.
		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		mock_validate_imp.assert_called_once_with(basic_plugin, imp = expected_imp)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [("make", ""), ("models", "")],
			params = mock_params,
		)
		basic_plugin.owner.ensure_models_exist.assert_called_once_with(
			make = mock_params["make"],
			models = expected_models,
		)
		# Expect the database to be updated
		basic_plugin.owner.db.execute.assert_called_once_with(ANY, (expected_imp,))
		basic_plugin.owner.call.assert_called_once_with(
			command = "set.firmware.model.imp",
			args = [*expected_models, f"make={mock_params['make']}", f"imp={expected_imp}"],
		)
		# Make sure cleanup was setup and then dismissed.
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.imp",
			args = [expected_imp],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()

	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run_no_make_or_models(
		self,
		mock_validate_args,
		mock_validate_imp,
		mock_exit_stack,
		mock_lowered,
		basic_plugin,
	):
		"""Test that run modifies the database as expected when no make or models are provided."""
		expected_imp = "foo"
		mock_args = [expected_imp]
		mock_params = {}
		mock_lowered.return_value = ("", "")

		basic_plugin.run(args = (mock_params, mock_args))

		# Make sure the arguments and parameters were validated.
		mock_validate_args.assert_called_once_with(basic_plugin, args = mock_args)
		mock_validate_imp.assert_called_once_with(basic_plugin, imp = expected_imp)
		basic_plugin.owner.fillParams.assert_called_once_with(
			names = [("make", ""), ("models", "")],
			params = mock_params,
		)
		basic_plugin.owner.ensure_models_exist.assert_not_called()
		# Expect the database to be updated
		basic_plugin.owner.db.execute.assert_called_once_with(ANY, (expected_imp,))
		basic_plugin.owner.call.assert_not_called()
		# Make sure cleanup was setup and then dismissed.
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.imp",
			args = [expected_imp],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_called_once_with()

	@pytest.mark.parametrize("failure_mock", ("ensure_models_exist", "validate_imp", "validate_args"))
	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run_errors(
		self,
		mock_validate_args,
		mock_validate_imp,
		mock_exit_stack,
		mock_lowered,
		failure_mock,
		basic_plugin,
	):
		"""Test that run fails if any of the params or args are invalid and does not touch the database."""
		mock_args = ["foo"]
		mock_params = {"make": "bar", "models": "baz, fizz, buzz"}
		mock_lowered.return_value = (param for param in mock_params.values())
		mock_validation_functions = {
			"ensure_models_exist": basic_plugin.owner.ensure_models_exist,
			"validate_imp": mock_validate_imp,
			"validate_args": mock_validate_args,
		}
		# Set the error on the correct mock validation function.
		mock_validation_functions[failure_mock].side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		# Expect the database to not be updated
		basic_plugin.owner.db.execute.assert_not_called()

	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.lowered", autospec = True)
	@patch(target = "stack.commands.add.firmware.imp.plugin_basic.ExitStack", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_imp", autospec = True)
	@patch.object(target = Plugin, attribute = "validate_args", autospec = True)
	def test_run_cleanup(
		self,
		mock_validate_args,
		mock_validate_imp,
		mock_exit_stack,
		mock_lowered,
		basic_plugin,
	):
		"""Test that run cleans up if setting the implementation relation fails."""
		mock_args = ["foo"]
		mock_params = {"make": "bar", "models": "baz, fizz, buzz"}
		mock_lowered.return_value = (param for param in mock_params.values())
		# Set the call to fail.
		basic_plugin.owner.call.side_effect = CommandError(cmd = basic_plugin.owner, msg = "Test error")

		with pytest.raises(CommandError):
			basic_plugin.run(args = (mock_params, mock_args))

		# Expect the cleanup to be set up, but not dismissed due to the error.
		mock_exit_stack.return_value.__enter__.return_value.callback.assert_called_once_with(
			basic_plugin.owner.call,
			command = "remove.firmware.imp",
			args = [mock_args[0].lower()],
		)
		mock_exit_stack.return_value.__enter__.return_value.pop_all.assert_not_called()
